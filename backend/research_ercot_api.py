"""Research ERCOT API - Find working endpoints with real data"""

import requests
import json
from datetime import datetime, timedelta
import time

# Credentials from .env
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
        print("[SUCCESS] Got access token")
        return token_data.get("id_token")
    else:
        print(f"[FAILED] Token error: {response.status_code}")
        print(response.text)
        return None

def test_data_endpoint(token, endpoint_path, params=None):
    """Test a specific endpoint to get actual data"""
    base_url = "https://api.ercot.com/api/public-reports"
    url = f"{base_url}/{endpoint_path}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Accept": "application/json"
    }

    print(f"\n[TESTING] {endpoint_path}")
    print(f"URL: {url}")
    if params:
        print(f"Params: {params}")

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()

                # Check if we got actual data or just metadata
                if isinstance(data, dict):
                    # Check for data vs metadata
                    if 'data' in data:
                        records = data['data']
                        if records:
                            print(f"[DATA FOUND] Got {len(records)} records in 'data' field")
                            print(f"Sample: {json.dumps(records[0] if isinstance(records, list) else records, indent=2)[:500]}")
                            return True
                    elif any(key in data for key in ['records', 'result', 'results']):
                        key = next(k for k in ['records', 'result', 'results'] if k in data)
                        records = data[key]
                        if records:
                            print(f"[DATA FOUND] Got {len(records)} records in '{key}' field")
                            print(f"Sample: {json.dumps(records[0] if isinstance(records, list) else records, indent=2)[:500]}")
                            return True
                    elif 'report' in str(data).lower() and 'description' in str(data).lower():
                        print("[METADATA] This is report metadata, not actual data")
                        return False
                    else:
                        print(f"[DATA STRUCTURE] Got response:")
                        print(json.dumps(data, indent=2)[:1000])
                        return True

                elif isinstance(data, list):
                    if len(data) > 0:
                        first_item = data[0]
                        # Check if it's metadata
                        if isinstance(first_item, dict) and 'reportTypeId' in first_item:
                            print("[METADATA] This is report metadata, not actual data")
                            return False
                        else:
                            print(f"[DATA FOUND] Got {len(data)} records")
                            print(f"Sample: {json.dumps(first_item, indent=2)[:500]}")
                            return True
                    else:
                        print("[EMPTY] No data returned")
                        return False

            except Exception as e:
                print(f"[ERROR] Failed to parse JSON: {e}")
                print(f"Raw response: {response.text[:500]}")
                return False
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            print(response.text[:500])
            return False

    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        return False

def main():
    """Research ERCOT API endpoints"""

    # Get token
    token = get_access_token()
    if not token:
        print("Failed to get token")
        return

    print("\n" + "="*60)
    print("RESEARCHING ERCOT API ENDPOINTS FOR REAL DATA")
    print("="*60)

    # Test different URL patterns based on ERCOT documentation
    test_cases = [
        # Try direct data access patterns
        ("np3-233-cd/data", None),
        ("np6-86-cd/data", None),
        ("np4-188-cd/data", None),

        # Try with explicit format
        ("np3-233-cd?format=json", None),
        ("np6-86-cd?format=json", None),

        # Try different date parameters
        ("np3-233-cd", {"deliveryDate": datetime.now().strftime("%Y-%m-%d")}),
        ("np3-233-cd", {"operatingDate": datetime.now().strftime("%Y-%m-%d")}),
        ("np3-233-cd", {"postingDate": datetime.now().strftime("%Y-%m-%d")}),

        # Try with date range
        ("np6-86-cd", {
            "deliveryDateFrom": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "deliveryDateTo": datetime.now().strftime("%Y-%m-%d")
        }),

        # Try different report IDs that might have real-time data
        ("np6-345-cd", None),  # Current Operating Plan
        ("np3-966-er", None),  # Real-Time Co-Optimization
        ("np6-787-cd", None),  # Real-Time ORDC

        # Try with timestamps
        ("np6-86-cd", {"SCEDTimestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}),

        # Try archive endpoints
        ("archive/np3-233-cd", {"operatingDate": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")}),

        # Try different base paths
        ("np3-233-cd/actual_system_load", None),
        ("np6-86-cd/system_conditions", None),
    ]

    working_endpoints = []

    for endpoint, params in test_cases:
        if test_data_endpoint(token, endpoint, params):
            working_endpoints.append((endpoint, params))
        time.sleep(0.5)  # Be polite to the API

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if working_endpoints:
        print(f"\n[SUCCESS] Found {len(working_endpoints)} endpoints with real data:")
        for endpoint, params in working_endpoints:
            print(f"  - {endpoint}")
            if params:
                print(f"    Params: {params}")
    else:
        print("\n[NOTICE] No endpoints returned actual data.")
        print("The ERCOT API may require:")
        print("  1. Different endpoint paths")
        print("  2. Specific query parameters")
        print("  3. Different authentication scope")
        print("  4. Paid subscription for data access")

    # Now let's try the Data API v1 endpoints
    print("\n" + "="*60)
    print("TRYING DATA API V1 ENDPOINTS")
    print("="*60)

    # Test v1 API pattern
    v1_base = "https://api.ercot.com/api/public-reports/v1"

    v1_endpoints = [
        "resource-data/rtm-lmp",
        "resource-data/dam-lmp",
        "resource-data/sced-data",
        "load-data/system-load",
        "load-data/forecast",
    ]

    for endpoint in v1_endpoints:
        url = f"{v1_base}/{endpoint}"
        print(f"\n[V1 TEST] {url}")

        headers = {
            "Authorization": f"Bearer {token}",
            "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
            "Accept": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.text[:500]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()