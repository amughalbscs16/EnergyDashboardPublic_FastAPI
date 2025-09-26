"""Test direct ERCOT dashboard API with real-time data"""

import asyncio
import httpx
import json

async def test_ercot_dashboard():
    """Test ERCOT's public dashboard endpoints"""

    async with httpx.AsyncClient() as client:
        # Test supply-demand endpoint
        print("Testing ERCOT Supply-Demand Dashboard...")
        url = "https://www.ercot.com/api/1/services/read/dashboards/supply-demand.json"

        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"SUCCESS! Got {len(data.get('data', []))} data points")
                print(f"Last Updated: {data.get('lastUpdated')}")

                # Show latest data
                if data.get('data'):
                    latest = data['data'][-1]
                    print(f"\nLatest Data Point:")
                    print(f"  Timestamp: {latest.get('timestamp')}")
                    print(f"  Demand: {latest.get('demand')} MW")
                    print(f"  Capacity: {latest.get('capacity')} MW")
                    print(f"  Reserve: {latest.get('capacity', 0) - latest.get('demand', 0)} MW")

                return data
            else:
                print(f"Failed: Status {response.status_code}")

        except Exception as e:
            print(f"Error: {e}")

    return None

async def test_fuel_mix():
    """Test ERCOT fuel mix endpoint"""

    async with httpx.AsyncClient() as client:
        print("\nTesting ERCOT Fuel Mix Dashboard...")
        url = "https://www.ercot.com/api/1/services/read/dashboards/fuel-mix.json"

        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"SUCCESS! Got fuel mix data")
                print(f"Last Updated: {data.get('lastUpdated')}")

                # Show today's generation
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")

                if data.get('data') and today in data['data']:
                    today_data = data['data'][today]
                    if today_data:
                        latest_time = sorted(today_data.keys())[-1]
                        latest = today_data[latest_time]

                        print(f"\nCurrent Generation Mix ({latest_time}):")
                        total = 0
                        for fuel_type, gen_data in latest.items():
                            if isinstance(gen_data, dict) and 'gen' in gen_data:
                                gen_mw = gen_data['gen']
                                print(f"  {fuel_type}: {gen_mw:,.0f} MW")
                                total += gen_mw
                        print(f"  TOTAL: {total:,.0f} MW")

                return data

        except Exception as e:
            print(f"Error: {e}")

    return None

if __name__ == "__main__":
    print("="*60)
    print("TESTING REAL-TIME ERCOT DATA ACCESS")
    print("="*60)

    # Run async tests
    loop = asyncio.get_event_loop()

    supply_data = loop.run_until_complete(test_ercot_dashboard())
    fuel_data = loop.run_until_complete(test_fuel_mix())

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if supply_data and fuel_data:
        print("✓ Both ERCOT dashboard endpoints working!")
        print("✓ Real-time data is accessible")
        print("\nData available:")
        print(f"  - Supply/Demand: {len(supply_data.get('data', []))} data points")
        print(f"  - Fuel Mix: Multiple fuel types with generation data")
    else:
        print("Some endpoints failed - check errors above")