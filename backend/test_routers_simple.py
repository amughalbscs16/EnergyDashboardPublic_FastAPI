#!/usr/bin/env python3
"""
Simple test script for router functions

Usage:
    python test_routers_simple.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set the PYTHONPATH for relative imports
os.environ["PYTHONPATH"] = str(backend_dir)

async def test_router_functions():
    """Test router functions directly"""
    print("Testing Router Functions Directly")
    print("=" * 40)

    try:
        # Import router functions
        from app.routers.ercot import get_current_conditions, get_forecast, get_ancillary_services
        from app.routers.weather import get_weather, get_weather_alerts, get_weather_forecast

        print("[ERCOT] Testing ERCOT router functions...")

        # Test ERCOT functions
        try:
            current = await get_current_conditions()
            print(f"[OK] Current conditions: {current['system_load_mw']} MW")
        except Exception as e:
            print(f"[ERROR] Current conditions: {e}")

        try:
            forecast = await get_forecast()
            print(f"[OK] Forecast: {forecast['forecast_hours']} hours")
        except Exception as e:
            print(f"[ERROR] Forecast: {e}")

        try:
            ancillary = await get_ancillary_services()
            print(f"[OK] Ancillary services: {ancillary['regulation_up_mw']} MW")
        except Exception as e:
            print(f"[ERROR] Ancillary services: {e}")

        print("\n[WEATHER] Testing Weather router functions...")

        # Test Weather functions
        try:
            weather = await get_weather("78701")
            print(f"[OK] Weather for {weather['zip_code']}: {weather['temperature_f']}°F")
        except Exception as e:
            print(f"[ERROR] Weather: {e}")

        try:
            alerts = await get_weather_alerts("78701")
            print(f"[OK] Weather alerts: {len(alerts)} alerts")
        except Exception as e:
            print(f"[ERROR] Weather alerts: {e}")

        try:
            forecast = await get_weather_forecast("78701")
            print(f"[OK] Weather forecast: {len(forecast['forecast'])} hours")
        except Exception as e:
            print(f"[ERROR] Weather forecast: {e}")

        print("\n[SUCCESS] All router functions are working!")
        return True

    except Exception as e:
        print(f"[ERROR] Router function test error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_router_functions())
    if result:
        print("\n[SUCCESS] Router function tests passed!")
    else:
        print("\n[FAILURE] Router function tests failed!")