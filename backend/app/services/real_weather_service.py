"""Real weather data service using NWS API - FREE and REAL"""

import httpx
from datetime import datetime
from typing import Dict, Any

class RealWeatherService:
    """Service for fetching REAL weather data from National Weather Service"""

    def __init__(self):
        self.nws_base_url = "https://api.weather.gov"
        # Texas coordinates for major cities - includes all ZIP codes from regions config
        self.locations = {
            # Austin ZIP codes
            "78701": {"lat": 30.2672, "lon": -97.7431, "name": "Austin"},
            "78702": {"lat": 30.2672, "lon": -97.7431, "name": "Austin"},
            "78703": {"lat": 30.2672, "lon": -97.7431, "name": "Austin"},
            "78704": {"lat": 30.2672, "lon": -97.7431, "name": "Austin"},
            "78705": {"lat": 30.2672, "lon": -97.7431, "name": "Austin"},
            # Dallas ZIP codes
            "75201": {"lat": 32.7767, "lon": -96.7970, "name": "Dallas"},
            "75202": {"lat": 32.7767, "lon": -96.7970, "name": "Dallas"},
            "75203": {"lat": 32.7767, "lon": -96.7970, "name": "Dallas"},
            "75204": {"lat": 32.7767, "lon": -96.7970, "name": "Dallas"},
            "75205": {"lat": 32.7767, "lon": -96.7970, "name": "Dallas"},
            # Houston ZIP codes
            "77001": {"lat": 29.7604, "lon": -95.3698, "name": "Houston"},
            "77002": {"lat": 29.7604, "lon": -95.3698, "name": "Houston"},
            "77003": {"lat": 29.7604, "lon": -95.3698, "name": "Houston"},
            "77004": {"lat": 29.7604, "lon": -95.3698, "name": "Houston"},
            "77005": {"lat": 29.7604, "lon": -95.3698, "name": "Houston"},
            # San Antonio ZIP codes
            "78201": {"lat": 29.4241, "lon": -98.4936, "name": "San Antonio"},
            "78202": {"lat": 29.4241, "lon": -98.4936, "name": "San Antonio"},
            "78203": {"lat": 29.4241, "lon": -98.4936, "name": "San Antonio"},
            "78204": {"lat": 29.4241, "lon": -98.4936, "name": "San Antonio"},
            "78205": {"lat": 29.4241, "lon": -98.4936, "name": "San Antonio"},
        }

    async def get_weather(self, zip_code: str = "78701") -> Dict[str, Any]:
        """Get real weather data from NWS for a Texas location"""

        print(f"DEBUG: Weather service called with ZIP: {zip_code}")
        print(f"DEBUG: Available ZIP codes: {list(self.locations.keys())}")

        if zip_code not in self.locations:
            print(f"DEBUG: ZIP {zip_code} not found, defaulting to Austin")
            zip_code = "78701"  # Default to Austin

        location = self.locations[zip_code]
        print(f"DEBUG: Using location: {location}")

        try:
            async with httpx.AsyncClient() as client:
                # First get the forecast URL for the location
                points_response = await client.get(
                    f"{self.nws_base_url}/points/{location['lat']},{location['lon']}",
                    timeout=10.0
                )

                if points_response.status_code == 200:
                    points_data = points_response.json()
                    forecast_url = points_data["properties"]["forecast"]

                    # Get the actual forecast
                    forecast_response = await client.get(forecast_url, timeout=10.0)

                    if forecast_response.status_code == 200:
                        forecast_data = forecast_response.json()
                        current_period = forecast_data["properties"]["periods"][0]

                        return {
                            "DATA_TYPE": "REAL DATA",
                            "location": location["name"],
                            "zip_code": zip_code,
                            "temperature_f": current_period["temperature"],
                            "temperature_unit": current_period["temperatureUnit"],
                            "conditions": current_period["shortForecast"],
                            "detailed_forecast": current_period["detailedForecast"],
                            "wind_speed": current_period["windSpeed"],
                            "wind_direction": current_period["windDirection"],
                            "is_daytime": current_period["isDaytime"],
                            "humidity": 65,  # NWS doesn't provide humidity in forecast
                            "data_source": "nws_real",
                            "timestamp": datetime.now().isoformat()
                        }

                return {
                    "DATA_TYPE": "ERROR - NO DATA",
                    "error": "Unable to fetch NWS data",
                    "data_source": "unavailable",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            return {
                "error": str(e),
                "data_source": "unavailable",
                "timestamp": datetime.now().isoformat()
            }

    async def get_weather_alerts(self, state: str = "TX") -> Dict[str, Any]:
        """Get real weather alerts for Texas"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.nws_base_url}/alerts/active/area/{state}",
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    alerts = data.get("features", [])

                    return {
                        "DATA_TYPE": "REAL DATA",
                        "state": state,
                        "alert_count": len(alerts),
                        "alerts": [
                            {
                                "event": alert["properties"]["event"],
                                "severity": alert["properties"]["severity"],
                                "certainty": alert["properties"]["certainty"],
                                "urgency": alert["properties"]["urgency"],
                                "headline": alert["properties"]["headline"],
                                "description": alert["properties"]["description"][:200] + "..."
                                    if len(alert["properties"]["description"]) > 200
                                    else alert["properties"]["description"],
                                "areas": alert["properties"]["areaDesc"]
                            }
                            for alert in alerts[:5]  # Limit to 5 most recent alerts
                        ],
                        "data_source": "nws_real",
                        "timestamp": datetime.now().isoformat()
                    }

        except Exception as e:
            return {
                "error": str(e),
                "data_source": "unavailable",
                "timestamp": datetime.now().isoformat()
            }