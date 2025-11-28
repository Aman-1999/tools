import asyncio
import aiohttp
import base64
from typing import List, Dict, Any, Optional
from loguru import logger
from config import settings
from models import RankingRequest, LocationData, OrganicResult, MapResult

class DataForSEOClient:
    """
    DataForSEO API client for organic and maps ranking data
    """

    def __init__(self):
        self.base_url = settings.dataforseo_url
        self.login = settings.dataforseo_login
        self.password = settings.dataforseo_password
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_session()

    async def create_session(self):
        """Create aiohttp session with authentication"""
        auth = aiohttp.BasicAuth(self.login, self.password)
        timeout = aiohttp.ClientTimeout(total=settings.request_timeout)

        self.session = aiohttp.ClientSession(
            auth=auth,
            timeout=timeout,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'RankTracker-Prototype/1.0'
            }
        )

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()

    async def test_connection(self) -> bool:
        """Test API connection"""
        try:
            url = f"{self.base_url}/serp/google/organic/live/advanced"

            # Simple test request
            test_task = [{
                "keyword": "test",
                "location_name": "United States",
                "language_name": "English",
                "device": "desktop",
                "depth": 1
            }]

            async with self.session.post(url, json=test_task) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('status_code') == 20000
                return False

        except Exception as e:
            logger.error(f"DataForSEO connection test failed: {e}")
            return False

    async def get_organic_rankings(self, request: RankingRequest, location: LocationData) -> List[OrganicResult]:
        """Get organic search rankings"""
        try:
            url = f"{self.base_url}/serp/google/organic/live/advanced"

            # Prepare task for DataForSEO
            task = {
                "keyword": request.keyword,
                "location_coordinate": f"{location.latitude},{location.longitude},17",
                "language_name": self._get_language_name(request.language_code),
                "device": request.device,
                "depth": request.depth,
                "calculate_rectangles": False,
                "include_serp_info": True
            }

            logger.info(f"Requesting organic rankings for: {request.keyword}")

            async with self.session.post(url, json=[task]) as response:
                if response.status != 200:
                    logger.error(f"DataForSEO API error: {response.status}")
                    return []

                data = await response.json()

                if not data.get('tasks') or len(data['tasks']) == 0:
                    logger.warning("No tasks returned from DataForSEO")
                    return []

                task_result = data['tasks'][0]

                if task_result.get('status_code') != 20000:
                    logger.error(f"Task failed: {task_result.get('status_message')}")
                    return []

                results = task_result.get('result', [])
                if not results:
                    logger.warning("No results in task response")
                    return []

                items = results[0].get('items', [])

                # Convert to our format
                organic_results = []
                for item in items:
                    if item.get('type') == 'organic':
                        result = OrganicResult(
                            position=item.get('rank_group', item.get('rank_absolute')),
                            title=item.get('title'),
                            description=item.get('description'),
                            url=item.get('url'),
                            domain=item.get('domain'),
                            breadcrumb=item.get('breadcrumb')
                        )
                        organic_results.append(result)

                logger.info(f"Found {len(organic_results)} organic results")
                return organic_results[:request.depth]

        except Exception as e:
            logger.error(f"Error getting organic rankings: {e}")
            return []

    async def get_maps_rankings(self, request: RankingRequest, location: LocationData) -> List[MapResult]:
        """Get Google Maps rankings"""
        try:
            url = f"{self.base_url}/serp/google/maps/live/advanced"

            # Prepare task for DataForSEO
            task = {
                "keyword": request.keyword,
                "location_coordinate": f"{location.latitude},{location.longitude},17",
                "language_name": self._get_language_name(request.language_code),
                "device": request.device,
                "depth": min(request.depth, 40)  # Maps API typically returns fewer results
            }

            logger.info(f"Requesting maps rankings for: {request.keyword}")

            async with self.session.post(url, json=[task]) as response:
                if response.status != 200:
                    logger.error(f"DataForSEO Maps API error: {response.status}")
                    return []

                data = await response.json()

                if not data.get('tasks') or len(data['tasks']) == 0:
                    logger.warning("No maps tasks returned from DataForSEO")
                    return []

                task_result = data['tasks'][0]

                if task_result.get('status_code') != 20000:
                    logger.error(f"Maps task failed: {task_result.get('status_message')}")
                    return []

                results = task_result.get('result', [])
                if not results:
                    logger.warning("No maps results in task response")
                    return []

                items = results[0].get('items', [])

                # Convert to our format
                map_results = []
                for item in items:
                    if item.get('type') == 'maps_paid' or item.get('type') == 'local_pack':
                        result = MapResult(
                            position=item.get('rank_group', item.get('rank_absolute')),
                            title=item.get('title'),
                            address=item.get('address'),
                            phone=item.get('phone'),
                            website=item.get('url'),
                            rating=item.get('rating', {}).get('rating_value') if item.get('rating') else None,
                            reviews_count=item.get('rating', {}).get('votes_count') if item.get('rating') else None,
                            category=item.get('category')
                        )
                        map_results.append(result)

                logger.info(f"Found {len(map_results)} maps results")
                return map_results[:request.depth]

        except Exception as e:
            logger.error(f"Error getting maps rankings: {e}")
            return []

    def _get_language_name(self, language_code: str) -> str:
        """Convert language code to DataForSEO language name"""
        language_map = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese'
        }
        return language_map.get(language_code.lower(), 'English')