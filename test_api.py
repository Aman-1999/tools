#!/usr/bin/env python3
"""
Test script for the Rank Tracker Prototype
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

async def test_api_endpoint(url: str, method: str = "GET", data: Dict[Any, Any] = None) -> Dict[str, Any]:
    """Test an API endpoint"""
    async with aiohttp.ClientSession() as session:
        try:
            if method.upper() == "POST":
                async with session.post(url, json=data) as response:
                    return {
                        "status": response.status,
                        "data": await response.json()
                    }
            else:
                async with session.get(url) as response:
                    return {
                        "status": response.status,
                        "data": await response.json()
                    }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

async def run_tests():
    """Run all tests"""
    base_url = "http://127.0.0.1:8000"

    print("🧪 Testing Rank Tracker Prototype API")
    print("=" * 50)

    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    health_result = await test_api_endpoint(f"{base_url}/health")
    print(f"   Status: {health_result['status']}")
    if health_result['status'] == 200:
        print("   ✅ Health check passed")
    else:
        print("   ❌ Health check failed")

    # Test 2: API Status
    print("\n2. Testing API status endpoint...")
    status_result = await test_api_endpoint(f"{base_url}/api/status")
    print(f"   Status: {status_result['status']}")
    if status_result['status'] == 200:
        print("   ✅ API status check passed")
        apis = status_result['data']
        for api_name, api_info in apis.items():
            print(f"     - {api_name}: {api_info['status']}")
    else:
        print("   ❌ API status check failed")

    # Test 3: Geocoding Test
    print("\n3. Testing geocoding...")
    geocoding_data = {
        "keyword": "test search",
        "location": {
            "address": "New York, NY",
            "pincode": "10001"
        },
        "device": "desktop",
        "language_code": "en",
        "depth": 5
    }

    print("   Testing with sample data:")
    print(f"   - Keyword: {geocoding_data['keyword']}")
    print(f"   - Location: {geocoding_data['location']['address']}")

    geocoding_result = await test_api_endpoint(f"{base_url}/api/check-rankings", "POST", geocoding_data)
    print(f"   Status: {geocoding_result['status']}")

    if geocoding_result['status'] == 200:
        print("   ✅ Geocoding and ranking check passed")
        data = geocoding_result['data']
        print(f"   📍 Geocoded to: {data['location']['latitude']}, {data['location']['longitude']}")
        print(f"   🔍 Found {len(data.get('organic_results', []))} organic results")
        print(f"   📍 Found {len(data.get('maps_results', []))} maps results")
    else:
        print("   ❌ Geocoding/ranking check failed")
        if 'error' in geocoding_result:
            print(f"   Error: {geocoding_result['error']}")
        elif 'data' in geocoding_result and 'detail' in geocoding_result['data']:
            print(f"   Error: {geocoding_result['data']['detail']}")

    # Test 4: Sample Rank Check (if APIs are working)
    if status_result['status'] == 200:
        print("\n4. Testing full ranking check...")
        ranking_data = {
            "keyword": "pizza restaurant",
            "location": {
                "address": "Chicago, IL",
                "pincode": "60601"
            },
            "device": "desktop",
            "language_code": "en",
            "depth": 10
        }

        print("   Testing with real search data:")
        print(f"   - Keyword: {ranking_data['keyword']}")
        print(f"   - Location: {ranking_data['location']['address']}")
        print("   - This may take 10-30 seconds...")

        ranking_result = await test_api_endpoint(f"{base_url}/api/check-rankings", "POST", ranking_data)
        print(f"   Status: {ranking_result['status']}")

        if ranking_result['status'] == 200:
            print("   ✅ Full ranking check passed")
            data = ranking_result['data']
            print(f"   ⏱️ Processing time: {data.get('processing_time_seconds', 'N/A')}s")
            print(f"   🔍 Organic results: {len(data.get('organic_results', []))}")
            print(f"   📍 Maps results: {len(data.get('maps_results', []))}")

            # Show first few results
            organic = data.get('organic_results', [])
            if organic:
                print("   📋 Sample organic results:")
                for i, result in enumerate(organic[:3], 1):
                    print(f"     {i}. {result.get('title', 'No title')} - {result.get('domain', 'No domain')}")

            maps = data.get('maps_results', [])
            if maps:
                print("   📋 Sample maps results:")
                for i, result in enumerate(maps[:3], 1):
                    print(f"     {i}. {result.get('title', 'No title')} - {result.get('address', 'No address')}")

        else:
            print("   ❌ Full ranking check failed")
            if 'error' in ranking_result:
                print(f"   Error: {ranking_result['error']}")
            elif 'data' in ranking_result and 'detail' in ranking_result['data']:
                print(f"   Error: {ranking_result['data']['detail']}")

    print("\n" + "=" * 50)
    print("🏁 Testing complete!")
    print("\n💡 Next steps:")
    print("   1. If tests pass ✅ - Your rank tracker is working!")
    print("   2. If tests fail ❌ - Check your .env file and API credentials")
    print("   3. Open http://127.0.0.1:8000 in your browser to use the web interface")
    print("   4. Check http://127.0.0.1:8000/docs for API documentation")

if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test runner error: {e}")
        print("Make sure the server is running: python main.py")