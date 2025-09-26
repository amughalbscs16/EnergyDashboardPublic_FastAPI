"""Test script to verify ERCOT real data fetching"""

import httpx
import asyncio
import json
from datetime import datetime

async def fetch_real_ercot_data():
    """Fetch REAL data from ERCOT public dashboard"""

    print("Fetching REAL ERCOT data from public dashboard...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Fetch supply-demand data
        supply_demand_url = "https://www.ercot.com/api/1/services/read/dashboards/supply-demand.json"

        try:
            response = await client.get(supply_demand_url)

            if response.status_code == 200:
                data = response.json()

                # Get the most recent data point
                if data.get('data') and len(data['data']) > 0:
                    latest = data['data'][-1]

                    result = {
                        "DATA_TYPE": "REAL DATA",
                        "system_load_mw": latest.get('demand', 0),
                        "system_capacity_mw": latest.get('capacity', 0),
                        "reserves_mw": latest.get('capacity', 0) - latest.get('demand', 0),
                        "timestamp": latest.get('timestamp'),
                        "data_source": "ercot_public_dashboard_live",
                        "last_updated": data.get('lastUpdated')
                    }

                    print("\nSUCCESS - REAL ERCOT DATA:")
                    print(json.dumps(result, indent=2))
                    return result
                else:
                    print("ERROR: No data in response")

            else:
                print(f"ERROR: HTTP {response.status_code}")

        except Exception as e:
            print(f"ERROR fetching: {e}")

    return None

# Run the test
if __name__ == "__main__":
    asyncio.run(fetch_real_ercot_data())