"""
Simple ERCOT Data Explorer Backend
Focused on DR (Demand Response) and DER (Distributed Energy Resources) data
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import httpx
import asyncio
from datetime import datetime, timedelta
import os
from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="ERCOT Data Explorer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ERCOT API Configuration
ERCOT_CONFIG = {
    "username": "your.email@example.com",
    "password": "YOUR_PASSWORD_HERE",
    "subscription_key": "YOUR_SUBSCRIPTION_KEY_HERE",
    "auth_url": "https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token",
    "client_id": "fec253ea-0d06-4272-a5e6-b478baeecd70",
    "base_url": "https://api.ercot.com/api/public-reports"
}

# Cache for token
_token_cache = {"token": None, "expires_at": None}

# Track failed requests for token refresh
_failed_requests_count = 0
_max_retry_attempts = 2

class ErcotEndpoint(BaseModel):
    name: str
    endpoint: str
    description: str
    category: str
    parameters: Optional[Dict[str, str]] = None

# DR and DER Related Endpoints
ERCOT_ENDPOINTS = [
    # Demand Response & Market Prices
    ErcotEndpoint(
        name="Real-Time System Conditions",
        endpoint="np6-86-cd",
        description="Real-time system conditions including frequency, load, and generation",
        category="DR",
        parameters={"deliveryDate": "Current date in YYYY-MM-DD format"}
    ),
    ErcotEndpoint(
        name="Day-Ahead Load Forecast",
        endpoint="np3-233-cd",
        description="Day-ahead load forecast for demand planning",
        category="DR",
        parameters={"deliveryDate": "Forecast date in YYYY-MM-DD format"}
    ),
    ErcotEndpoint(
        name="Real-Time Settlement Point Prices",
        endpoint="np6-905-cd/spp_node_zone_hub",
        description="Real-time Settlement Point Prices at nodes, zones and hubs (15-min)",
        category="DR",
        parameters=None
    ),
    ErcotEndpoint(
        name="DAM Settlement Point Prices",
        endpoint="np4-190-cd/dam_stlmnt_pnt_prices",
        description="Day-ahead market settlement point prices hourly",
        category="DR",
        parameters=None
    ),
    ErcotEndpoint(
        name="DAM Shadow Prices",
        endpoint="np4-191-cd/dam_shadow_prices",
        description="Day-ahead market shadow prices for constraints",
        category="DR",
        parameters=None
    ),
    ErcotEndpoint(
        name="2-Day Load Summary",
        endpoint="np3-910-er/2d_agg_load_summary",
        description="2-day aggregated load summary by area",
        category="DR",
        parameters=None
    ),

    # DER & Generation Related
    ErcotEndpoint(
        name="Solar Power Production",
        endpoint="np4-737-cd",
        description="Solar power production forecast and actuals",
        category="DER",
        parameters={"deliveryDate": "Date in YYYY-MM-DD format"}
    ),
    ErcotEndpoint(
        name="Wind Power Production",
        endpoint="np4-732-cd",
        description="Wind power production forecast and actuals",
        category="DER",
        parameters={"deliveryDate": "Date in YYYY-MM-DD format"}
    ),
    ErcotEndpoint(
        name="2-Day Generation Summary",
        endpoint="np3-910-er/2d_agg_gen_summary",
        description="2-day aggregated generation summary by fuel type",
        category="DER",
        parameters=None
    ),
    ErcotEndpoint(
        name="DAM Generation Resources",
        endpoint="np3-966-er/60_dam_gen_res_as_offers",
        description="60-day delayed DAM generation resources AS offers",
        category="DER",
        parameters=None
    ),
    ErcotEndpoint(
        name="SCED Generation Resources",
        endpoint="np3-965-er/60_sced_smne_gen_res",
        description="60-day delayed SCED generation resources",
        category="DER",
        parameters=None
    ),
    ErcotEndpoint(
        name="DAM Hourly LMP",
        endpoint="np4-183-cd/dam_hourly_lmp",
        description="Day-ahead market hourly locational marginal prices",
        category="DER",
        parameters=None
    ),

    # Grid Operations & Ancillary Services
    ErcotEndpoint(
        name="SCED Shadow Prices",
        endpoint="np6-86-cd/shdw_prices_bnd_trns_const",
        description="SCED shadow prices for binding transmission constraints",
        category="Grid",
        parameters=None
    ),
    ErcotEndpoint(
        name="DAM Load Resources",
        endpoint="np3-966-er/60_dam_load_res_as_offers",
        description="60-day delayed DAM load resources AS offers",
        category="Grid",
        parameters=None
    ),
    ErcotEndpoint(
        name="2-Day DSR Loads",
        endpoint="np3-910-er/2d_agg_dsr_loads",
        description="2-day aggregated demand-side response loads",
        category="Grid",
        parameters=None
    ),
]

def get_access_token(force_refresh: bool = False) -> Optional[str]:
    """Get or refresh ERCOT OAuth access token

    Args:
        force_refresh: If True, get a new token even if cached one exists
    """
    global _failed_requests_count
    now = datetime.now()

    # Check if we have a valid cached token (unless force refresh)
    if not force_refresh and _token_cache["token"] and _token_cache["expires_at"]:
        # Add 5 minute buffer before expiry
        if _token_cache["expires_at"] > now + timedelta(minutes=5):
            return _token_cache["token"]

    print(f"[{now.isoformat()}] Refreshing ERCOT authentication token...")

    # Get new token
    auth_data = {
        "username": ERCOT_CONFIG["username"],
        "password": ERCOT_CONFIG["password"],
        "grant_type": "password",
        "scope": f"openid {ERCOT_CONFIG['client_id']} offline_access",
        "client_id": ERCOT_CONFIG["client_id"],
        "response_type": "id_token"
    }

    try:
        response = requests.post(
            ERCOT_CONFIG["auth_url"],
            data=auth_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )

        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("id_token")

            # Cache token (use expires_in if provided, else default to 55 minutes)
            expires_in = token_data.get("expires_in", 3300)  # Default to 55 minutes
            # Ensure expires_in is an integer
            if isinstance(expires_in, str):
                expires_in = int(expires_in)
            _token_cache["token"] = token
            _token_cache["expires_at"] = now + timedelta(seconds=expires_in)

            # Reset failed requests counter on successful token refresh
            _failed_requests_count = 0

            print(f"[{now.isoformat()}] Token refreshed successfully. Expires at {_token_cache['expires_at'].isoformat()}")
            return token
        else:
            print(f"Token error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Exception getting token: {e}")
        return None

def fetch_ercot_data(endpoint: str, params: Optional[Dict] = None, retry_count: int = 0) -> Dict[str, Any]:
    """Fetch data from ERCOT API endpoint with automatic retry and token refresh

    Args:
        endpoint: The ERCOT API endpoint
        params: Optional query parameters
        retry_count: Current retry attempt (used internally)
    """
    global _failed_requests_count

    # Force token refresh if we've had failures
    force_refresh = retry_count > 0 or _failed_requests_count >= 2

    token = get_access_token(force_refresh=force_refresh)
    if not token:
        raise HTTPException(status_code=401, detail="Failed to authenticate with ERCOT")

    url = f"{ERCOT_CONFIG['base_url']}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Ocp-Apim-Subscription-Key": ERCOT_CONFIG["subscription_key"],
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)

        # Handle 401 Unauthorized - token might be expired
        if response.status_code == 401 and retry_count < _max_retry_attempts:
            print(f"Got 401 Unauthorized for {endpoint}, refreshing token and retrying...")
            _failed_requests_count += 1
            # Clear the cached token to force refresh
            _token_cache["token"] = None
            _token_cache["expires_at"] = None
            # Retry with fresh token
            return fetch_ercot_data(endpoint, params, retry_count + 1)

        if response.status_code == 200:
            # Reset failed counter on successful request
            _failed_requests_count = 0
            data = response.json()

            # Check if this is metadata response with artifacts
            if isinstance(data, dict) and "artifacts" in data and data["artifacts"]:
                # Get the actual data endpoint from artifacts
                artifact = data["artifacts"][0]
                if "_links" in artifact and "endpoint" in artifact["_links"]:
                    data_url = artifact["_links"]["endpoint"]["href"]

                    # Fetch actual data from the artifact endpoint
                    data_response = requests.get(data_url, headers=headers, params=params, timeout=30)

                    if data_response.status_code == 200:
                        actual_data = data_response.json()
                        return {
                            "success": True,
                            "endpoint": endpoint,
                            "data": actual_data,
                            "metadata": data,
                            "data_url": data_url,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "success": True,
                            "endpoint": endpoint,
                            "data": data,
                            "note": "Got metadata, but couldn't fetch actual data",
                            "data_status": data_response.status_code,
                            "timestamp": datetime.now().isoformat()
                        }

            # Return data as-is if no artifacts found
            return {
                "success": True,
                "endpoint": endpoint,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "endpoint": endpoint,
                "error": f"HTTP {response.status_code}",
                "message": response.text[:500],
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        return {
            "success": False,
            "endpoint": endpoint,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/")
def root():
    """API root endpoint"""
    return {
        "name": "ERCOT Data Explorer",
        "version": "1.0.0",
        "description": "Explore ERCOT DR and DER data possibilities",
        "endpoints": {
            "/endpoints": "List all available ERCOT endpoints",
            "/explore/{endpoint}": "Fetch data from specific endpoint",
            "/dr-data": "Get Demand Response related data",
            "/der-data": "Get Distributed Energy Resources data",
            "/test-all": "Test all endpoints to see what data is available",
            "/test-token": "Test ERCOT API authentication",
            "/refresh-token": "Force refresh ERCOT authentication token",
            "/realtime/supply-demand": "Get real-time supply and demand data",
            "/realtime/fuel-mix": "Get real-time generation fuel mix"
        }
    }

@app.get("/test-token")
def test_token():
    """Test ERCOT API authentication and return token status"""
    try:
        token = get_access_token(force_refresh=False)
        if token:
            # Test the token with a simple request
            test_url = f"{ERCOT_CONFIG['base_url']}/np3-233-cd"
            headers = {
                "Authorization": f"Bearer {token}",
                "Ocp-Apim-Subscription-Key": ERCOT_CONFIG["subscription_key"],
                "Accept": "application/json"
            }

            response = requests.get(test_url, headers=headers, timeout=10)

            return {
                "success": True,
                "message": "Authentication successful",
                "token_obtained": True,
                "token_length": len(token),
                "token_expires_at": _token_cache["expires_at"].isoformat() if _token_cache["expires_at"] else None,
                "token_valid_for": str(_token_cache["expires_at"] - datetime.now()) if _token_cache["expires_at"] else None,
                "test_endpoint_status": response.status_code,
                "test_endpoint_response": response.text[:200] if response.status_code == 200 else response.text[:200],
                "credentials": {
                    "username": ERCOT_CONFIG["username"],
                    "subscription_key": ERCOT_CONFIG["subscription_key"][:10] + "...",
                    "auth_url": ERCOT_CONFIG["auth_url"],
                    "client_id": ERCOT_CONFIG["client_id"]
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to obtain token",
                "token_obtained": False,
                "credentials": {
                    "username": ERCOT_CONFIG["username"],
                    "auth_url": ERCOT_CONFIG["auth_url"]
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Exception during authentication"
        }

@app.get("/refresh-token")
def refresh_token():
    """Force refresh ERCOT authentication token"""
    try:
        # Force token refresh
        token = get_access_token(force_refresh=True)

        if token:
            return {
                "success": True,
                "message": "Token refreshed successfully",
                "token_expires_at": _token_cache["expires_at"].isoformat() if _token_cache["expires_at"] else None,
                "token_valid_for": str(_token_cache["expires_at"] - datetime.now()) if _token_cache["expires_at"] else None,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "Failed to refresh token",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/endpoints")
def list_endpoints():
    """List all configured ERCOT endpoints"""
    return {
        "total": len(ERCOT_ENDPOINTS),
        "categories": {
            "DR": [e.model_dump() for e in ERCOT_ENDPOINTS if e.category == "DR"],
            "DER": [e.model_dump() for e in ERCOT_ENDPOINTS if e.category == "DER"],
            "Grid": [e.model_dump() for e in ERCOT_ENDPOINTS if e.category == "Grid"]
        }
    }

@app.get("/explore/{endpoint:path}")
def explore_endpoint(endpoint: str, date: Optional[str] = None):
    """Explore a specific ERCOT endpoint"""
    # Find endpoint config
    endpoint_config = next((e for e in ERCOT_ENDPOINTS if e.endpoint == endpoint), None)

    params = {}
    if date:
        # Try common date parameters
        for param in ["deliveryDate", "operatingDate", "postingDate"]:
            params[param] = date
    elif endpoint_config and endpoint_config.parameters:
        # Use default parameters if specified
        if "deliveryDate" in endpoint_config.parameters:
            params["deliveryDate"] = datetime.now().strftime("%Y-%m-%d")

    result = fetch_ercot_data(endpoint, params)

    # Add metadata about the endpoint
    if endpoint_config:
        result["metadata"] = endpoint_config.model_dump()

    return result

@app.get("/dr-data")
def get_dr_data(date: Optional[str] = None):
    """Get all Demand Response related data"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    results = {}
    dr_endpoints = [e for e in ERCOT_ENDPOINTS if e.category == "DR"]

    for endpoint in dr_endpoints:
        params = {"deliveryDate": date} if endpoint.parameters else None
        results[endpoint.name] = fetch_ercot_data(endpoint.endpoint, params)

    return {
        "category": "Demand Response",
        "date": date,
        "endpoints_queried": len(dr_endpoints),
        "results": results
    }

@app.get("/der-data")
def get_der_data(date: Optional[str] = None):
    """Get all Distributed Energy Resources data"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    results = {}
    der_endpoints = [e for e in ERCOT_ENDPOINTS if e.category == "DER"]

    for endpoint in der_endpoints:
        params = {"deliveryDate": date} if endpoint.parameters else None
        results[endpoint.name] = fetch_ercot_data(endpoint.endpoint, params)

    return {
        "category": "Distributed Energy Resources",
        "date": date,
        "endpoints_queried": len(der_endpoints),
        "results": results
    }

@app.get("/test-all")
def test_all_endpoints():
    """Test all endpoints to see what data is available"""
    results = {
        "summary": {
            "total_endpoints": len(ERCOT_ENDPOINTS),
            "successful": 0,
            "failed": 0,
            "with_data": 0,
            "empty": 0
        },
        "endpoints": {}
    }

    for endpoint in ERCOT_ENDPOINTS:
        params = {}
        if endpoint.parameters and "deliveryDate" in endpoint.parameters:
            params["deliveryDate"] = datetime.now().strftime("%Y-%m-%d")

        result = fetch_ercot_data(endpoint.endpoint, params)

        # Analyze result
        if result["success"]:
            results["summary"]["successful"] += 1

            # Check if we got actual data
            if "data" in result and result["data"]:
                data = result["data"]

                # Check various data structures
                has_data = False
                data_count = 0

                if isinstance(data, dict):
                    for key in ["data", "records", "result", "results"]:
                        if key in data and data[key]:
                            has_data = True
                            data_count = len(data[key]) if isinstance(data[key], list) else 1
                            break
                elif isinstance(data, list):
                    has_data = len(data) > 0
                    data_count = len(data)

                if has_data:
                    results["summary"]["with_data"] += 1
                else:
                    results["summary"]["empty"] += 1

                # Store simplified result
                results["endpoints"][endpoint.name] = {
                    "success": True,
                    "has_data": has_data,
                    "data_count": data_count,
                    "sample": str(data)[:200] if has_data else None,
                    "endpoint": endpoint.endpoint,
                    "category": endpoint.category
                }
            else:
                results["summary"]["empty"] += 1
                results["endpoints"][endpoint.name] = {
                    "success": True,
                    "has_data": False,
                    "endpoint": endpoint.endpoint,
                    "category": endpoint.category
                }
        else:
            results["summary"]["failed"] += 1
            results["endpoints"][endpoint.name] = {
                "success": False,
                "error": result.get("error"),
                "endpoint": endpoint.endpoint,
                "category": endpoint.category
            }

    return results

@app.get("/realtime/supply-demand")
async def get_realtime_supply_demand():
    """Get real-time supply and demand data from ERCOT public dashboard"""
    url = "https://www.ercot.com/api/1/services/read/dashboards/supply-demand.json"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()

                # Process and enhance the data
                if data.get('data'):
                    latest = data['data'][-1] if data['data'] else None
                    if latest:
                        latest['reserve'] = latest.get('capacity', 0) - latest.get('demand', 0)
                        latest['reserve_percentage'] = (latest['reserve'] / latest.get('capacity', 1)) * 100 if latest.get('capacity') else 0

                return {
                    "success": True,
                    "source": "ERCOT Public Dashboard",
                    "data": data,
                    "latest": latest if 'latest' in locals() else None,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

@app.get("/realtime/fuel-mix")
async def get_realtime_fuel_mix():
    """Get real-time generation fuel mix from ERCOT public dashboard"""
    url = "https://www.ercot.com/api/1/services/read/dashboards/fuel-mix.json"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()

                # Get today's latest data
                today = datetime.now().strftime("%Y-%m-%d")
                latest_data = None

                if data.get('data') and today in data['data']:
                    today_data = data['data'][today]
                    if today_data:
                        latest_time = sorted(today_data.keys())[-1]
                        latest_data = {
                            "time": latest_time,
                            "generation": today_data[latest_time],
                            "total": sum(
                                gen_data.get('gen', 0)
                                for gen_data in today_data[latest_time].values()
                                if isinstance(gen_data, dict)
                            )
                        }

                return {
                    "success": True,
                    "source": "ERCOT Public Dashboard",
                    "data": data,
                    "latest": latest_data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

@app.get("/realtime/all")
async def get_all_realtime_data():
    """Get all real-time data from ERCOT"""
    supply_demand = await get_realtime_supply_demand()
    fuel_mix = await get_realtime_fuel_mix()

    return {
        "supply_demand": supply_demand,
        "fuel_mix": fuel_mix,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/public/generation-outages")
async def get_generation_outages():
    """Get real-time generation outages data"""
    url = "https://www.ercot.com/api/1/services/read/dashboards/generation-outages.json"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "source": "ERCOT Public Dashboard",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

@app.get("/public/daily-prc")
async def get_daily_prc():
    """Get daily Physical Responsive Capability (PRC) data"""
    url = "https://www.ercot.com/api/1/services/read/dashboards/daily-prc.json"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "source": "ERCOT Public Dashboard",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


@app.get("/public/solar-power-production")
async def get_solar_power():
    """Get solar power production data from combined wind/solar endpoint"""
    url = "https://www.ercot.com/api/1/services/read/dashboards/combine-wind-solar.json"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                # Extract just solar data
                solar_data = {}
                if "currentDay" in data and "data" in data["currentDay"]:
                    for timestamp, hour_data in data["currentDay"]["data"].items():
                        solar_data[timestamp] = {
                            "actualSolar": hour_data.get("actualSolar"),
                            "copHslSolar": hour_data.get("copHslSolar"),
                            "stppf": hour_data.get("stppf"),
                            "pvgrpp": hour_data.get("pvgrpp"),
                            "timestamp": hour_data.get("timestamp")
                        }
                return {
                    "success": True,
                    "source": "ERCOT Combined Wind/Solar Dashboard",
                    "data": solar_data,
                    "full_data": data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

@app.get("/public/wind-power-production")
async def get_wind_power():
    """Get wind power production data from combined wind/solar endpoint"""
    url = "https://www.ercot.com/api/1/services/read/dashboards/combine-wind-solar.json"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                # Extract just wind data
                wind_data = {}
                if "currentDay" in data and "data" in data["currentDay"]:
                    for timestamp, hour_data in data["currentDay"]["data"].items():
                        wind_data[timestamp] = {
                            "actualWind": hour_data.get("actualWind"),
                            "copHslWind": hour_data.get("copHslWind"),
                            "stwpf": hour_data.get("stwpf"),
                            "wgrpp": hour_data.get("wgrpp"),
                            "timestamp": hour_data.get("timestamp")
                        }
                return {
                    "success": True,
                    "source": "ERCOT Combined Wind/Solar Dashboard",
                    "data": wind_data,
                    "full_data": data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)