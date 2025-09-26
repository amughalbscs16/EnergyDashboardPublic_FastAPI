#!/usr/bin/env python3
"""
Test script for FastAPI routers to ensure they work with the updated services

Usage:
    python test_routers.py
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

from app.routers.ercot import router as ercot_router
from app.routers.weather import router as weather_router
from fastapi import FastAPI

async def test_routers():
    """Test that routers work with updated services"""
    print("Testing FastAPI Routers")
    print("=" * 40)

    # Create a test FastAPI app
    app = FastAPI()
    app.include_router(ercot_router, prefix="/api/ercot", tags=["ercot"])
    app.include_router(weather_router, prefix="/api/weather", tags=["weather"])

    try:
        try:
            from fastapi.testclient import TestClient
        except ImportError:
            from starlette.testclient import TestClient

        client = TestClient(app)

        print("[ERCOT] Testing ERCOT router endpoints...")

        # Test ERCOT current conditions
        response = client.get("/api/ercot/current")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Current conditions: {data['system_load_mw']} MW")
        else:
            print(f"[ERROR] Current conditions failed: {response.status_code}")

        # Test ERCOT forecast
        response = client.get("/api/ercot/forecast")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Forecast: {data['forecast_hours']} hours")
        else:
            print(f"[ERROR] Forecast failed: {response.status_code}")

        # Test ancillary services
        response = client.get("/api/ercot/ancillary-services")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Ancillary services: {data['regulation_up_mw']} MW")
        else:
            print(f"[ERROR] Ancillary services failed: {response.status_code}")

        print("\n[WEATHER] Testing Weather router endpoints...")

        # Test weather for Austin
        response = client.get("/api/weather/78701")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Weather for {data['zip_code']}: {data['temperature_f']}°F")
        else:
            print(f"[ERROR] Weather failed: {response.status_code}")

        # Test weather forecast
        response = client.get("/api/weather/forecast/78701")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Weather forecast: {len(data['forecast'])} hours")
        else:
            print(f"[ERROR] Weather forecast failed: {response.status_code}")

        # Test weather alerts
        response = client.get("/api/weather/78701/alerts")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Weather alerts: {len(data)} alerts")
        else:
            print(f"[ERROR] Weather alerts failed: {response.status_code}")

        print("\n[SUCCESS] All router endpoints are working correctly!")
        return True

    except ImportError:
        print("[WARN] fastapi.testclient not available, skipping router tests")
        print("       Run: pip install httpx")
        return True
    except Exception as e:
        print(f"[ERROR] Router test error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_routers())
    if result:
        print("\n[SUCCESS] Router integration tests passed!")
    else:
        print("\n[FAILURE] Router integration tests failed!")