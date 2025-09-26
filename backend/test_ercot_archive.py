"""Test ERCOT Archive API to get actual data files"""

import requests
import json
from datetime import datetime, timedelta

# Credentials
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
        return None

def get_archive_data(token, report_id):
    """Get archive data from ERCOT"""

    archive_url = f"https://api.ercot.com/api/public-reports/archive/{report_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Accept": "application/json"
    }

    print(f"\nFetching archive for: {report_id}")
    print(f"URL: {archive_url}")

    try:
        response = requests.get(archive_url, headers=headers)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Check if we have archives
            if 'archives' in data:
                archives = data['archives']
                print(f"Found {len(archives)} archive entries")

                # Get the most recent archive
                if archives:
                    latest = archives[0]
                    print(f"\nLatest archive:")
                    print(f"  Date: {latest.get('explodedDate', 'N/A')}")
                    print(f"  Doc ID: {latest.get('docId', 'N/A')}")

                    # Check for download links
                    if 'links' in latest:
                        for link in latest['links']:
                            print(f"  Link: {link.get('rel', '')}: {link.get('href', '')}")

                            # Try to download the actual data
                            if link.get('rel') == 'data' or 'csv' in link.get('href', '').lower():
                                download_url = link['href']
                                print(f"\n  Attempting to download data from: {download_url}")

                                # Download the actual data file
                                download_response = requests.get(download_url, headers=headers)
                                if download_response.status_code == 200:
                                    # Check if it's CSV data
                                    content_type = download_response.headers.get('content-type', '')
                                    print(f"  Content-Type: {content_type}")

                                    # Show first 500 characters of data
                                    content = download_response.text[:500]
                                    print(f"  DATA PREVIEW:\n{content}")
                                    return True
                                else:
                                    print(f"  Download failed: {download_response.status_code}")

            else:
                print("No 'archives' field in response")
                print(f"Response keys: {data.keys()}")

        else:
            print(f"Error: {response.text[:500]}")

    except Exception as e:
        print(f"Exception: {e}")

    return False

def main():
    """Test ERCOT Archive API"""

    token = get_access_token()
    if not token:
        return

    print("\n" + "="*60)
    print("TESTING ERCOT ARCHIVE API FOR ACTUAL DATA")
    print("="*60)

    # List of report IDs that should have recent data
    report_ids = [
        "np3-233-cd",    # System Load by Weather Zone
        "np6-86-cd",     # Real-time System Conditions
        "np4-188-cd",    # Settlement Point Prices
        "np6-787-cd",    # Real-time ORDC
        "np6-788-cd",    # Real-time LMP
        "np3-565-cd",    # 7-day Load Forecast
        "np4-732-cd",    # DAM Settlement Point Prices
        "np4-745-cd",    # Solar Power Production
        "np4-742-cd",    # Wind Power Production
    ]

    found_data = []

    for report_id in report_ids:
        if get_archive_data(token, report_id):
            found_data.append(report_id)

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if found_data:
        print(f"\n[SUCCESS] Found actual data for {len(found_data)} reports:")
        for report_id in found_data:
            print(f"  - {report_id}")
    else:
        print("\n[NOTICE] No actual data downloads succeeded")
        print("This might mean:")
        print("  1. Data is available but requires different authentication")
        print("  2. Data download URLs are protected/private")
        print("  3. Need to use ERCOT's data portal instead of API")

if __name__ == "__main__":
    main()