"""Real ERCOT data service - fetches from ERCOT API Explorer"""

import os
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import time
import requests

class RealERCOTService:
    """Service for fetching REAL ERCOT data from API Explorer"""

    def __init__(self):
        self.public_api_key = os.getenv("ERCOT_PUBLIC_API_KEY")
        self.esr_api_key = os.getenv("ERCOT_ESR_API_KEY")
        self.username = os.getenv("ERCOT_USERNAME")
        self.password = os.getenv("ERCOT_PASSWORD")

        print(f"DEBUG: RealERCOTService initialized")
        print(f"DEBUG: Has username: {bool(self.username)}")
        print(f"DEBUG: Has password: {bool(self.password)}")
        print(f"DEBUG: Has public API key: {bool(self.public_api_key)}")

        # ERCOT API Explorer endpoints
        self.base_url = "https://api.ercot.com/api/public-reports"
        self.auth_url = "https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token"
        self.client_id = "fec253ea-0d06-4272-a5e6-b478baeecd70"

        # Token management
        self.access_token = None
        self.token_expiry = None

        # Get initial token
        self._get_access_token()

        # Headers for API calls
        self.headers = self._get_headers()
        self.esr_headers = self._get_headers(use_esr=True)

    def _get_access_token(self) -> Optional[str]:
        """Get OAuth access token from ERCOT"""
        if not self.username or not self.password:
            print("ERCOT username or password not configured")
            return None

        # Check if token is still valid
        if self.access_token and self.token_expiry:
            if time.time() < self.token_expiry:
                return self.access_token

        try:
            # Prepare OAuth request as form data
            auth_data = {
                "username": self.username,
                "password": self.password,
                "grant_type": "password",
                "scope": f"openid {self.client_id} offline_access",
                "client_id": self.client_id,
                "response_type": "id_token"
            }

            # Send as form data (not URL params)
            response = requests.post(
                self.auth_url,
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("id_token")  # ERCOT uses id_token as bearer token
                # Token is valid for 1 hour
                self.token_expiry = time.time() + 3600
                print("Successfully obtained ERCOT access token")
                return self.access_token
            else:
                print(f"Failed to get ERCOT token: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Error getting ERCOT access token: {e}")
            return None

    def _get_headers(self, use_esr: bool = False) -> Dict[str, str]:
        """Get headers with current access token"""
        headers = {
            "Accept": "application/json",
            "Ocp-Apim-Subscription-Key": self.esr_api_key if use_esr else self.public_api_key
        }

        # Add Bearer token if available
        token = self._get_access_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    async def get_current_conditions(self) -> Dict[str, Any]:
        """Get current ERCOT grid conditions from REAL dashboard API"""

        print("DEBUG: get_current_conditions called")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Use ERCOT's public dashboard JSON API for real-time data
                supply_demand_url = "https://www.ercot.com/api/1/services/read/dashboards/supply-demand.json"
                daily_prc_url = "https://www.ercot.com/api/1/services/read/dashboards/daily-prc.json"

                try:
                    # Fetch supply-demand data
                    response = await client.get(supply_demand_url)

                    if response.status_code == 200:
                        supply_data = response.json()

                        # Get the most recent data point
                        if supply_data.get('data') and len(supply_data['data']) > 0:
                            # Get the last data point (most recent)
                            latest = supply_data['data'][-1]

                            # Fetch PRC (Physical Responsive Capability) data
                            prc_response = await client.get(daily_prc_url)
                            prc_data = prc_response.json() if prc_response.status_code == 200 else {}

                            current_prc = 0
                            if prc_data.get('current_condition'):
                                prc_value = prc_data['current_condition'].get('prc_value', '0')
                                # Remove commas and convert to float
                                current_prc = float(prc_value.replace(',', ''))

                            # Calculate reserves (capacity - demand)
                            capacity = float(latest.get('capacity', 0))
                            demand = float(latest.get('demand', 0))
                            reserves = capacity - demand

                            return {
                                "system_load_mw": round(demand, 0),
                                "system_capacity_mw": round(capacity, 0),
                                "reserves_mw": round(reserves, 0),
                                "operating_reserves_mw": round(current_prc, 0),
                                "data_source": "ercot_dashboard_live",
                                "api_status": "connected",
                                "timestamp": latest.get('timestamp', datetime.now().isoformat()),
                                "last_updated": supply_data.get('lastUpdated', 'unknown')
                            }
                except Exception as e:
                    print(f"Error fetching ERCOT dashboard data: {e}")
                    import traceback
                    traceback.print_exc()

        except Exception as e:
            print(f"Error connecting to ERCOT API: {e}")
            import traceback
            traceback.print_exc()

        # No synthetic data - return error state
        return {
            "error": "ERCOT API data unavailable",
            "data_source": "none",
            "api_status": "disconnected",
            "timestamp": datetime.now().isoformat()
        }

    async def _get_current_price_from_spp(self, client: httpx.AsyncClient) -> float:
        """Get current price from real-time SPP data"""
        # Without access to real-time pricing API that doesn't require complex parsing,
        # we cannot provide accurate pricing data
        return None  # No synthetic price data

    async def _get_reserves(self, client: httpx.AsyncClient) -> float:
        """Get current operating reserves"""
        try:
            # NP3-965-ER: Total ERCOT Ancillary Service Offers
            url = f"{self.base_url}/np3-965-er/as_offers"
            response = await client.get(url, headers=self._get_headers())

            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    latest = data[-1]
                    return float(latest.get("REGUP", 4200))
        except:
            pass

        return 0.0


    async def get_forecast(self) -> Dict[str, Any]:
        """Get ERCOT forecast data from dashboard API"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get supply-demand forecast data
                url = "https://www.ercot.com/api/1/services/read/dashboards/supply-demand.json"
                response = await client.get(url)

                if response.status_code == 200:
                    data = response.json()

                    if data.get('data'):
                        # Extract next 24 hours of data (5-minute intervals = 288 points)
                        # Take hourly samples for 24-hour forecast
                        forecast_data = data['data'][:288:12]  # Every 12th point = hourly

                        load_values = []

                        for entry in forecast_data[:24]:  # Limit to 24 hours
                            demand = float(entry.get('demand', 0))
                            load_values.append(round(demand, 0))

                        peak_load = max(load_values) if load_values else 0
                        peak_hour = load_values.index(peak_load) if load_values and peak_load > 0 else 0

                        return {
                            "forecast_hours": list(range(24)),
                            "load_forecast_mw": load_values,
                            "peak_load_mw": peak_load,
                            "peak_hour": peak_hour,
                            "data_source": "ercot_dashboard_forecast",
                            "timestamp": datetime.now().isoformat(),
                            "last_updated": data.get('lastUpdated', 'unknown')
                        }
        except Exception as e:
            print(f"Error fetching forecast: {e}")

        # No synthetic data - return error state
        return {
            "error": "ERCOT forecast data unavailable",
            "data_source": "none",
            "timestamp": datetime.now().isoformat()
        }


    async def get_renewable_generation(self) -> Dict[str, Any]:
        """Get current renewable generation data from fuel mix API"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get fuel mix data which includes wind and solar
                url = "https://www.ercot.com/api/1/services/read/dashboards/fuel-mix.json"
                response = await client.get(url)

                if response.status_code == 200:
                    data = response.json()

                    # Get today's date
                    today = datetime.now().strftime("%Y-%m-%d")

                    if data.get('data') and today in data['data']:
                        # Get the most recent timestamp for today
                        today_data = data['data'][today]
                        if today_data:
                            # Get the last timestamp's data
                            latest_timestamp = sorted(today_data.keys())[-1]
                            latest = today_data[latest_timestamp]

                            wind_output = float(latest.get("Wind", {}).get("gen", 0))
                            solar_output = float(latest.get("Solar", {}).get("gen", 0))

                            return {
                                "wind_output_mw": round(wind_output, 0),
                                "solar_output_mw": round(solar_output, 0),
                                "total_renewable_mw": round(wind_output + solar_output, 0),
                                "data_source": "ercot_fuel_mix_live",
                                "timestamp": latest_timestamp,
                                "last_updated": data.get('lastUpdated', 'unknown')
                            }
        except Exception as e:
            print(f"Error fetching renewable data: {e}")

        # No synthetic data - return error state
        return {
            "error": "ERCOT renewable data unavailable",
            "data_source": "none",
            "timestamp": datetime.now().isoformat()
        }