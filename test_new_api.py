#!/usr/bin/env python3
"""Test script for new real data API endpoints"""

import requests
import json
from datetime import datetime

# Test on port 8002
BASE_URL = "http://localhost:8002"

def test_endpoints():
    print("Testing New Real Data API on port 8001")
    print("=" * 50)

    # Test root
    print("\n1. Root endpoint:")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test health
    print("\n2. Health endpoint:")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Health check: OK")
    except Exception as e:
        print(f"   Error: {e}")

    # Test ERCOT current
    print("\n3. ERCOT Current Conditions:")
    try:
        response = requests.get(f"{BASE_URL}/api/ercot/current")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   System Load: {data.get('system_load_mw'):,} MW")
            print(f"   Price: ${data.get('price_per_mwh'):.2f}/MWh")
            renewable = data.get('renewable_output_mw', {})
            print(f"   Wind: {renewable.get('wind', 0):,} MW")
            print(f"   Solar: {renewable.get('solar', 0):,} MW")
    except Exception as e:
        print(f"   Error: {e}")

    # Test Weather
    print("\n4. Weather Data (Austin - 78701):")
    try:
        response = requests.get(f"{BASE_URL}/api/weather/78701")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Temperature: {data.get('temperature_f')}°F")
            print(f"   Humidity: {data.get('humidity_pct')}%")
            print(f"   Conditions: {data.get('conditions')}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test Cohorts
    print("\n5. Cohort Data:")
    try:
        response = requests.get(f"{BASE_URL}/api/cohorts/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            cohorts = response.json()
            print(f"   Total cohorts: {len(cohorts)}")
            total_accounts = sum(c['num_accounts'] for c in cohorts)
            total_flex = sum(c['num_accounts'] * c['flex_kw_per_account'] / 1000 for c in cohorts)
            print(f"   Total accounts: {total_accounts:,}")
            print(f"   Total flexibility: {total_flex:,.1f} MW")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "=" * 50)
    print("Test Complete!")

if __name__ == "__main__":
    test_endpoints()