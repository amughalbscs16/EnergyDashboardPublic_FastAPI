"""Simple ERCOT service that fetches REAL data from public dashboard"""

import httpx
from datetime import datetime
from typing import Dict, Any

class SimpleERCOTService:
    """Service for fetching REAL ERCOT data from public dashboard"""

    def __init__(self):
        self.supply_demand_url = "https://www.ercot.com/api/1/services/read/dashboards/supply-demand.json"
        self.daily_prc_url = "https://www.ercot.com/api/1/services/read/dashboards/daily-prc.json"

    async def get_current_conditions(self) -> Dict[str, Any]:
        """Get current ERCOT grid conditions - REAL DATA"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch supply-demand data
                response = await client.get(self.supply_demand_url)

                if response.status_code == 200:
                    data = response.json()

                    # Get the most recent data point
                    if data.get('data') and len(data['data']) > 0:
                        # Get current data (look for most recent non-forecast)
                        current_data = None
                        for point in reversed(data['data']):
                            if point.get('demand', 0) > 0:  # Real data has demand
                                current_data = point
                                break

                        if not current_data:
                            current_data = data['data'][-1]

                        demand = float(current_data.get('demand', 0))
                        capacity = float(current_data.get('capacity', 0))

                        return {
                            "DATA_TYPE": "REAL DATA",
                            "system_load_mw": round(demand, 0),
                            "system_capacity_mw": round(capacity, 0),
                            "reserves_mw": round(capacity - demand, 0),
                            "reserve_margin_pct": round((capacity - demand) / demand * 100, 2) if demand > 0 else 0,
                            "timestamp": current_data.get('timestamp', datetime.now().isoformat()),
                            "data_source": "ercot_public_dashboard",
                            "api_status": "connected",
                            "last_updated": data.get('lastUpdated', 'unknown')
                        }

        except Exception as e:
            print(f"Error fetching ERCOT data: {e}")

        # Return error state
        return {
            "DATA_TYPE": "ERROR - NO DATA",
            "error": "Unable to fetch ERCOT data",
            "data_source": "unavailable",
            "api_status": "disconnected",
            "timestamp": datetime.now().isoformat()
        }

    async def get_forecast(self) -> Dict[str, Any]:
        """Get ERCOT load forecast - REAL DATA"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.supply_demand_url)

                if response.status_code == 200:
                    data = response.json()

                    # Extract forecast data (future timestamps)
                    now = datetime.now()
                    forecasts = []

                    if data.get('data'):
                        for point in data['data']:
                            # Add forecast points
                            forecasts.append({
                                "timestamp": point.get('timestamp'),
                                "forecast_mw": point.get('forecast', 0),
                                "demand_mw": point.get('demand', 0)
                            })

                    return {
                        "DATA_TYPE": "REAL DATA",
                        "forecast_data": forecasts[:48],  # Next 48 data points
                        "data_source": "ercot_public_dashboard",
                        "last_updated": data.get('lastUpdated')
                    }

        except Exception as e:
            print(f"Error fetching forecast: {e}")

        return {
            "DATA_TYPE": "ERROR - NO DATA",
            "error": "Unable to fetch forecast",
            "data_source": "unavailable"
        }

    async def get_real_time_prices(self) -> Dict[str, Any]:
        """Get real-time prices - LIMITED DATA AVAILABLE"""

        # ERCOT public dashboard doesn't provide real-time prices
        # Would need authenticated API access for this
        return {
            "DATA_TYPE": "NOT AVAILABLE",
            "note": "Real-time price data requires ERCOT authenticated API access",
            "alternative": "Use ERCOT's public price reports at ercot.com",
            "data_source": "unavailable"
        }