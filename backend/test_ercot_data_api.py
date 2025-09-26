"""Test ERCOT Data Portal API - Try to get actual real-time data"""

import requests
import json
from datetime import datetime

# Test without auth first to see what's publicly available
def test_public_endpoints():
    """Test public ERCOT endpoints that might not need auth"""

    endpoints = [
        # Try data.ercot.com endpoints
        "https://data.ercot.com/api/v1/current-conditions",
        "https://data.ercot.com/api/v1/real-time/system-conditions",
        "https://data.ercot.com/api/v1/reports/12300",  # Real-Time System Conditions report ID

        # Try direct CDR endpoints
        "https://www.ercot.com/content/cdr/html/real_time_system_conditions.html",
        "https://www.ercot.com/api/1/services/read/dashboards/daily-prc.json",
        "https://www.ercot.com/api/1/services/read/dashboards/fuel-mix.json",
        "https://www.ercot.com/api/1/services/read/dashboards/supply-demand.json",

        # Try MIS public API
        "https://www.ercot.com/misapp/servlets/IceDocListJsonWS",
        "https://www.ercot.com/misapp/GetReports.do?reportTypeId=12300",

        # Try content delivery endpoints
        "https://www.ercot.com/content/cdr/html/real_time_spp",
        "https://www.ercot.com/content/cdr/html/hb_busavg",
    ]

    print("Testing public endpoints for real-time data...")
    print("="*60)

    for url in endpoints:
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                print(f"Content-Type: {content_type}")

                if 'json' in content_type:
                    try:
                        data = response.json()
                        print(f"[JSON DATA] Found!")
                        print(json.dumps(data, indent=2)[:500])
                    except:
                        print("[JSON] Failed to parse")
                elif 'html' in content_type:
                    # Look for data in HTML
                    content = response.text
                    if 'lastUpdated' in content or 'data' in content[:1000]:
                        print("[HTML] Contains data indicators")
                        # Extract any JSON embedded in HTML
                        if 'var data' in content or 'var chart' in content:
                            print("[HTML] Has embedded data variables")
                else:
                    # Show raw content sample
                    print(f"Raw content: {response.text[:200]}")

        except Exception as e:
            print(f"Error: {str(e)[:100]}")

    print("\n" + "="*60)

def test_authenticated_data_api():
    """Test with authentication on data.ercot.com"""

    USERNAME = "your.email@example.com"
    PASSWORD = "YOUR_PASSWORD_HERE"
    SUBSCRIPTION_KEY = "YOUR_SUBSCRIPTION_KEY_HERE"

    print("\nTesting authenticated data.ercot.com API...")
    print("="*60)

    # Try different authentication approaches
    headers_options = [
        {"Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY},
        {"X-API-Key": SUBSCRIPTION_KEY},
        {"Authorization": f"Bearer {SUBSCRIPTION_KEY}"},
    ]

    test_urls = [
        "https://data.ercot.com/api/public/np3-233-cd",
        "https://data.ercot.com/api/public-reports/np3-233-cd",
        "https://data.ercot.com/fm/public/np3-233-cd",
    ]

    for headers in headers_options:
        for url in test_urls:
            print(f"\nURL: {url}")
            print(f"Headers: {list(headers.keys())}")

            try:
                response = requests.get(url, headers=headers, timeout=5)
                print(f"Status: {response.status_code}")

                if response.status_code == 200:
                    print("[SUCCESS] Got data!")
                    if response.text:
                        print(response.text[:300])

            except Exception as e:
                print(f"Error: {str(e)[:50]}")

if __name__ == "__main__":
    test_public_endpoints()
    test_authenticated_data_api()