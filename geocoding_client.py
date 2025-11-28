import asyncio
from typing import Optional, Tuple, Dict, Any
from geopy.geocoders import Nominatim, GoogleV3
from opencage.geocoder import OpenCageGeocode
from loguru import logger
from config import settings
from models import LocationInput, LocationData

class GeocodingClient:
    """
    Geocoding client with multiple provider fallback
    """

    def __init__(self):
        self.google_api_key = settings.google_maps_api_key
        self.opencage_api_key = settings.opencage_api_key

        # Initialize primary geocoder (Google if available, otherwise OpenCage)
        self.primary_geocoder = None
        self.fallback_geocoder = None
        self.free_geocoder = Nominatim(user_agent="RankTracker-Prototype/1.0")

        self._setup_geocoders()

    def _setup_geocoders(self):
        """Setup primary and fallback geocoders based on available API keys"""
        if self.google_api_key:
            try:
                self.primary_geocoder = GoogleV3(
                    api_key=self.google_api_key,
                    user_agent="RankTracker-Prototype/1.0"
                )
                logger.info("Google Maps geocoder initialized as primary")
            except Exception as e:
                logger.warning(f"Failed to initialize Google geocoder: {e}")

        if self.opencage_api_key:
            try:
                fallback_or_primary = OpenCageGeocode(self.opencage_api_key)
                if self.primary_geocoder is None:
                    self.primary_geocoder = fallback_or_primary
                    logger.info("OpenCage geocoder initialized as primary")
                else:
                    self.fallback_geocoder = fallback_or_primary
                    logger.info("OpenCage geocoder initialized as fallback")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenCage geocoder: {e}")

        if self.primary_geocoder is None:
            self.primary_geocoder = self.free_geocoder
            logger.info("Using free Nominatim geocoder as primary")

    async def geocode_location(self, location_input: LocationInput) -> LocationData:
        """
        Geocode location input to coordinates with fallback providers
        """
        # Build query string
        query_parts = [location_input.address]
        if location_input.pincode:
            query_parts.append(location_input.pincode)
        if location_input.city:
            query_parts.append(location_input.city)
        if location_input.country:
            query_parts.append(location_input.country)

        query = ", ".join(query_parts)

        logger.info(f"Geocoding location: {query}")

        # Try primary geocoder
        result = await self._geocode_with_provider(query, self.primary_geocoder, "primary")
        if result:
            return self._create_location_data(location_input, result, query)

        # Try fallback geocoder
        if self.fallback_geocoder:
            result = await self._geocode_with_provider(query, self.fallback_geocoder, "fallback")
            if result:
                return self._create_location_data(location_input, result, query)

        # Try free geocoder as last resort
        if self.primary_geocoder != self.free_geocoder:
            result = await self._geocode_with_provider(query, self.free_geocoder, "free")
            if result:
                return self._create_location_data(location_input, result, query)

        # If all fail, raise exception
        raise ValueError(f"Could not geocode location: {query}")

    async def _geocode_with_provider(self, query: str, geocoder, provider_name: str) -> Optional[Tuple[float, float, Dict[str, Any]]]:
        """
        Try to geocode with a specific provider
        """
        try:
            if isinstance(geocoder, OpenCageGeocode):
                # OpenCage is synchronous but we run it in executor
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(None, geocoder.geocode, query)

                if results and len(results) > 0:
                    location = results[0]
                    lat = location['geometry']['lat']
                    lng = location['geometry']['lng']
                    components = location.get('components', {})

                    logger.info(f"Successfully geocoded with {provider_name}: {lat}, {lng}")
                    return lat, lng, components

            else:
                # GeoPy geocoders
                loop = asyncio.get_event_loop()
                location = await loop.run_in_executor(None, geocoder.geocode, query)

                if location:
                    lat = location.latitude
                    lng = location.longitude

                    # Extract components from raw data
                    components = {}
                    if hasattr(location, 'raw'):
                        raw = location.raw
                        if 'address_components' in raw:
                            for component in raw['address_components']:
                                types = component.get('types', [])
                                if 'locality' in types:
                                    components['city'] = component['long_name']
                                elif 'country' in types:
                                    components['country'] = component['long_name']
                        elif 'display_name' in raw:
                            # Nominatim format
                            parts = raw['display_name'].split(', ')
                            if len(parts) >= 2:
                                components['city'] = parts[-3] if len(parts) > 2 else parts[0]
                                components['country'] = parts[-1]

                    logger.info(f"Successfully geocoded with {provider_name}: {lat}, {lng}")
                    return lat, lng, components

        except Exception as e:
            logger.warning(f"Geocoding failed with {provider_name}: {e}")

        return None

    def _create_location_data(self, location_input: LocationInput, result: Tuple[float, float, Dict[str, Any]], original_query: str) -> LocationData:
        """
        Create LocationData from geocoding result
        """
        lat, lng, components = result

        return LocationData(
            address=original_query,
            pincode=location_input.pincode,
            latitude=lat,
            longitude=lng,
            city=components.get('city') or location_input.city,
            country=components.get('country') or location_input.country
        )

    async def get_status(self) -> Dict[str, Any]:
        """
        Get status of all geocoding providers
        """
        status = {
            "status": "unknown",
            "providers": []
        }

        # Test primary geocoder
        if self.primary_geocoder:
            provider_name = type(self.primary_geocoder).__name__
            test_result = await self._test_geocoder(self.primary_geocoder, provider_name)
            status["providers"].append({
                "name": provider_name,
                "type": "primary",
                "status": "working" if test_result else "error"
            })

        # Test fallback geocoder
        if self.fallback_geocoder:
            provider_name = type(self.fallback_geocoder).__name__
            test_result = await self._test_geocoder(self.fallback_geocoder, provider_name)
            status["providers"].append({
                "name": provider_name,
                "type": "fallback",
                "status": "working" if test_result else "error"
            })

        # Test free geocoder if it's not already the primary
        if self.primary_geocoder != self.free_geocoder:
            test_result = await self._test_geocoder(self.free_geocoder, "Nominatim")
            status["providers"].append({
                "name": "Nominatim",
                "type": "free",
                "status": "working" if test_result else "error"
            })

        # Determine overall status
        working_providers = [p for p in status["providers"] if p["status"] == "working"]
        status["status"] = "working" if working_providers else "error"

        return status

    async def _test_geocoder(self, geocoder, provider_name: str) -> bool:
        """
        Test if a geocoder is working
        """
        try:
            result = await self._geocode_with_provider("New York, NY", geocoder, provider_name)
            return result is not None
        except:
            return False