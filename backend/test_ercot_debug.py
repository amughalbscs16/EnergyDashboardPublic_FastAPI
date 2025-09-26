#!/usr/bin/env python3
"""Direct test of ERCOT dashboard API"""

import asyncio
import httpx
import json

async def test_ercot_dashboard():
    """Test ERCOT dashboard API directly"""

    async with httpx.AsyncClient(timeout=30.0) as client:
        url = "https://www.ercot.com/api/1/services/read/dashboards/supply-demand.json"

        try:
            print(f"Testing URL: {url}")
            response = await client.get(url)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"SUCCESS! Got data with keys: {list(data.keys())}")

                if data.get('data'):
                    print(f"Data array has {len(data['data'])} items")
                    print(f"Last updated: {data.get('lastUpdated')}")

                    # Show latest data point
                    latest = data['data'][-1]
                    print(f"Latest data:")
                    print(f"  Timestamp: {latest.get('timestamp')}")
                    print(f"  Demand: {latest.get('demand')} MW")
                    print(f"  Capacity: {latest.get('capacity')} MW")

                return True
            else:
                print(f"HTTP Error: {response.status_code}")
                print(f"Response text: {response.text[:500]}")

        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()

    return False

if __name__ == "__main__":
    print("Testing ERCOT Dashboard API directly...")
    print("=" * 50)

    success = asyncio.run(test_ercot_dashboard())

    if success:
        print("\n✓ ERCOT API is working - data retrieved successfully")
    else:
        print("\n✗ ERCOT API test failed")