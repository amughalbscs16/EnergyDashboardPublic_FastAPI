"""Test ERCOT API endpoints with authentication"""

import requests
import json
import os
from datetime import datetime, timedelta

# Load credentials
USERNAME = "your.email@example.com"
PASSWORD = "YOUR_PASSWORD_HERE"
SUBSCRIPTION_KEY = "YOUR_SUBSCRIPTION_KEY_HERE"

# OAuth configuration
AUTH_URL = "https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token"
CLIENT_ID = "fec253ea-0d06-4272-a5e6-b478baeecd70"

def get_access_token():
    """Get OAuth access token"""
    auth_data = {
        "username": USERNAME,
        "password": PASSWORD,
        "grant_type": "password",
        "scope": f"openid {CLIENT_ID} offline_access",
        "client_id": CLIENT_ID,
        "response_type": "id_token"
    }

    response = requests.post(
        AUTH_URL,
        data=auth_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code == 200:
        token_data = response.json()
        print("[SUCCESS] Successfully obtained access token")
        return token_data.get("id_token")
    else:
        print(f"[FAILED] Failed to get token: {response.status_code}")
        print(response.text)
        return None

def test_endpoint(url, token, name):
    """Test an ERCOT API endpoint"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Accept": "application/json"
    }

    print(f"\n[TEST] Testing: {name}")
    print(f"   URL: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"   [SUCCESS] Got {len(data)} records")
                print(f"   Sample: {json.dumps(data[0] if data else {}, indent=2)[:500]}...")
                return True
            elif isinstance(data, dict):
                print(f"   [SUCCESS] Got response")
                print(f"   Data: {json.dumps(data, indent=2)[:500]}...")
                return True
            else:
                print(f"   [WARNING] Empty or unexpected response")
                return False
        else:
            print(f"   [ERROR] Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False

    except Exception as e:
        print(f"   [EXCEPTION] {str(e)}")
        return False

def main():
    """Test various ERCOT API endpoints"""

    # Get access token
    token = get_access_token()
    if not token:
        print("Failed to get access token. Exiting.")
        return

    # Base URLs
    base_url = "https://api.ercot.com/api/public-reports"

    # Calculate date parameters
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    # Format dates
    date_str = today.strftime("%Y-%m-%d")

    # List of endpoints to test
    endpoints = [
        # === Real-time data ===
        (f"{base_url}/np6-86-cd", "Real-Time System Conditions"),
        (f"{base_url}/np3-233-cd", "System Load by Weather Zone"),
        (f"{base_url}/np4-188-cd", "Settlement Point Prices"),
        (f"{base_url}/np6-787-cd", "Real-Time ORDC"),
        (f"{base_url}/np6-788-cd", "Real-Time LMP"),

        # === With date parameters ===
        (f"{base_url}/np6-86-cd?deliveryDate={date_str}", "System Conditions (with date)"),
        (f"{base_url}/np3-233-cd?operatingDay={date_str}", "Load by Zone (with date)"),

        # === Forecasts ===
        (f"{base_url}/np3-565-cd", "7-Day Load Forecast"),
        (f"{base_url}/np4-745-cd", "Solar Power Production"),
        (f"{base_url}/np4-742-cd", "Wind Power Production"),

        # === Archive endpoints ===
        (f"{base_url}/archive/np6-86-cd", "Archived System Conditions"),
        (f"{base_url}/archive/np3-233-cd", "Archived Load by Zone"),
    ]

    # Test each endpoint
    successful = []
    failed = []

    for url, name in endpoints:
        success = test_endpoint(url, token, name)
        if success:
            successful.append((url, name))
        else:
            failed.append((url, name))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"\n[SUCCESS] Working endpoints ({len(successful)}):")
    for url, name in successful:
        print(f"   - {name}")

    print(f"\n[FAILED] Non-working endpoints ({len(failed)}):")
    for url, name in failed:
        print(f"   - {name}")

if __name__ == "__main__":
    main()