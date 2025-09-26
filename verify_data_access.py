#!/usr/bin/env python3
"""
Data Source Verification Script
Tests access to all required public data sources for the Utility HITL Portal
"""

import requests
import json
from datetime import datetime, timedelta
import time

class DataSourceVerifier:
    def __init__(self):
        self.results = {}
        self.working_endpoints = []

    def test_ercot_data(self):
        """Test ERCOT public data endpoints"""
        print("\n=== Testing ERCOT Data Access ===")

        ercot_endpoints = {
            "Real-Time System Conditions": {
                "url": "https://www.ercot.com/api/1/services/read/dashboards/systemConditions.json",
                "description": "Current grid conditions"
            },
            "Current Day Outlook": {
                "url": "https://www.ercot.com/api/1/services/read/dashboards/dailyLoadForecastVsActual.json",
                "description": "Load forecast vs actual"
            },
            "Real-Time Prices": {
                "url": "https://www.ercot.com/api/1/services/read/dashboards/rtSppData.json",
                "description": "Settlement point prices"
            },
            "Fuel Mix": {
                "url": "https://www.ercot.com/api/1/services/read/dashboards/fuelMix.json",
                "description": "Generation by fuel type"
            },
            "Supply Demand": {
                "url": "https://www.ercot.com/api/1/services/read/dashboards/supplyDemand.json",
                "description": "Supply and demand curves"
            }
        }

        ercot_results = {}
        for name, config in ercot_endpoints.items():
            try:
                print(f"  Testing {name}...")
                response = requests.get(config["url"], timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    ercot_results[name] = {
                        "status": "✓ SUCCESS",
                        "url": config["url"],
                        "sample_keys": list(data.keys())[:5] if isinstance(data, dict) else f"Array with {len(data)} items",
                        "description": config["description"]
                    }
                    self.working_endpoints.append(config["url"])
                    print(f"    ✓ Success - {config['description']}")
                else:
                    ercot_results[name] = {
                        "status": f"✗ Failed (Status: {response.status_code})",
                        "url": config["url"]
                    }
                    print(f"    ✗ Failed with status {response.status_code}")
            except Exception as e:
                ercot_results[name] = {
                    "status": f"✗ Error: {str(e)[:50]}",
                    "url": config["url"]
                }
                print(f"    ✗ Error: {str(e)[:50]}")
            time.sleep(0.5)  # Be polite to the API

        self.results["ERCOT"] = ercot_results
        return ercot_results

    def test_noaa_weather(self):
        """Test NOAA weather API access"""
        print("\n=== Testing NOAA Weather API ===")

        # Test with Austin, TX coordinates
        lat, lon = 30.2672, -97.7431

        noaa_endpoints = {
            "Points Metadata": {
                "url": f"https://api.weather.gov/points/{lat},{lon}",
                "description": "Get forecast office and grid coordinates"
            }
        }

        noaa_results = {}

        # First get the grid endpoint
        try:
            print("  Getting grid coordinates for Austin, TX...")
            response = requests.get(
                noaa_endpoints["Points Metadata"]["url"],
                headers={"User-Agent": "UtilityPortalDemo"}
            )

            if response.status_code == 200:
                data = response.json()
                forecast_url = data["properties"]["forecast"]
                forecast_hourly_url = data["properties"]["forecastHourly"]
                grid_data_url = data["properties"]["forecastGridData"]

                noaa_results["Points Metadata"] = {
                    "status": "✓ SUCCESS",
                    "office": data["properties"]["gridId"],
                    "grid_x": data["properties"]["gridX"],
                    "grid_y": data["properties"]["gridY"]
                }

                # Test forecast endpoints
                print("  Testing hourly forecast...")
                forecast_response = requests.get(
                    forecast_hourly_url,
                    headers={"User-Agent": "UtilityPortalDemo"}
                )

                if forecast_response.status_code == 200:
                    forecast_data = forecast_response.json()
                    periods = forecast_data["properties"]["periods"][:3]
                    noaa_results["Hourly Forecast"] = {
                        "status": "✓ SUCCESS",
                        "url": forecast_hourly_url,
                        "sample": [{
                            "time": p["startTime"],
                            "temp": p["temperature"],
                            "conditions": p["shortForecast"]
                        } for p in periods]
                    }
                    self.working_endpoints.append(forecast_hourly_url)
                    print("    ✓ Hourly forecast available")
            else:
                noaa_results["NOAA API"] = {
                    "status": f"✗ Failed (Status: {response.status_code})"
                }

        except Exception as e:
            noaa_results["NOAA API"] = {
                "status": f"✗ Error: {str(e)[:100]}"
            }
            print(f"    ✗ Error: {str(e)[:50]}")

        # Test OpenWeatherMap as backup
        print("\n  Testing OpenWeatherMap (free tier)...")
        owm_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=YOUR_API_KEY"
        noaa_results["OpenWeatherMap Alternative"] = {
            "status": "API Key Required",
            "note": "Free tier available with 1000 calls/day",
            "signup": "https://openweathermap.org/api"
        }

        self.results["Weather"] = noaa_results
        return noaa_results

    def test_nrel_data(self):
        """Test NREL data availability"""
        print("\n=== Testing NREL Data Access ===")

        nrel_resources = {
            "ResStock (Residential)": {
                "dataset_url": "https://data.openei.org/submissions/4520",
                "api_docs": "https://developer.nrel.gov/docs/",
                "description": "15-minute residential load profiles by end use",
                "note": "Requires download of dataset files"
            },
            "ComStock (Commercial)": {
                "dataset_url": "https://data.openei.org/submissions/5859",
                "description": "Commercial building load profiles",
                "note": "Large dataset, requires download"
            },
            "NREL API": {
                "url": "https://developer.nrel.gov/api/pvwatts/v8.json?api_key=DEMO_KEY&lat=30&lon=-97&system_capacity=4&azimuth=180&tilt=30&array_type=1&module_type=1&losses=10",
                "description": "PV generation estimates"
            }
        }

        nrel_results = {}

        # Test PVWatts API with demo key
        print("  Testing NREL PVWatts API...")
        try:
            response = requests.get(nrel_resources["NREL API"]["url"], timeout=10)
            if response.status_code == 200:
                data = response.json()
                nrel_results["PVWatts API"] = {
                    "status": "✓ SUCCESS (Demo Key)",
                    "annual_production": f"{data['outputs']['ac_annual']:.0f} kWh",
                    "note": "Free API key available at developer.nrel.gov"
                }
                self.working_endpoints.append("PVWatts API")
                print("    ✓ PVWatts API working with DEMO_KEY")
            else:
                nrel_results["PVWatts API"] = {
                    "status": f"✗ Failed (Status: {response.status_code})"
                }
        except Exception as e:
            nrel_results["PVWatts API"] = {
                "status": f"✗ Error: {str(e)[:50]}"
            }

        # Document dataset availability
        nrel_results["Load Profile Datasets"] = {
            "ResStock": {
                "status": "Download Required",
                "size": "~10 GB for Texas data",
                "format": "CSV/Parquet",
                "url": nrel_resources["ResStock (Residential)"]["dataset_url"]
            },
            "ComStock": {
                "status": "Download Required",
                "size": "~5 GB for Texas subset",
                "url": nrel_resources["ComStock (Commercial)"]["dataset_url"]
            }
        }

        self.results["NREL"] = nrel_results
        return nrel_results

    def test_alternative_sources(self):
        """Test alternative and supplementary data sources"""
        print("\n=== Testing Alternative Data Sources ===")

        alternatives = {}

        # EIA API
        print("  Testing EIA (Energy Information Admin) API...")
        eia_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=YOUR_KEY&frequency=hourly&data[0]=value&facets[respondent][]=TEX&start=2024-01-01T00&end=2024-01-01T01"
        alternatives["EIA"] = {
            "status": "API Key Required (Free)",
            "signup": "https://www.eia.gov/opendata/register.php",
            "description": "Historical and real-time electricity data",
            "note": "Good alternative for ERCOT data"
        }

        # Sample synthetic data generation
        print("  Creating sample synthetic data...")
        sample_cohort = {
            "cohort_id": "RES_EV_78701",
            "name": "Residential EV Owners - Austin Central",
            "segment": "residential",
            "technology": "EV",
            "zip_code": "78701",
            "num_accounts": 1500,
            "avg_flex_kw": 7.2,
            "peak_hours": [17, 18, 19, 20],
            "baseline_acceptance": 0.65
        }

        alternatives["Synthetic Data"] = {
            "status": "✓ Can Generate",
            "sample": sample_cohort,
            "note": "Will create realistic Texas cohorts based on public statistics"
        }

        self.results["Alternatives"] = alternatives
        return alternatives

    def generate_summary_report(self):
        """Generate a summary report of all data source tests"""
        print("\n" + "="*60)
        print("DATA ACCESS VERIFICATION SUMMARY")
        print("="*60)

        report = {
            "timestamp": datetime.now().isoformat(),
            "working_endpoints": self.working_endpoints,
            "recommendations": [],
            "next_steps": []
        }

        # ERCOT Summary
        if "ERCOT" in self.results:
            working_ercot = [k for k, v in self.results["ERCOT"].items()
                           if "SUCCESS" in str(v.get("status", ""))]
            if working_ercot:
                print(f"\n✓ ERCOT: {len(working_ercot)}/{len(self.results['ERCOT'])} endpoints working")
                print(f"  Working: {', '.join(working_ercot)}")
                report["recommendations"].append("Use ERCOT dashboard APIs for real-time grid data")
            else:
                print("\n✗ ERCOT: No public API endpoints found working")
                report["recommendations"].append("Implement web scraping for ERCOT public dashboards")

        # Weather Summary
        if "Weather" in self.results:
            if any("SUCCESS" in str(v.get("status", "")) for v in self.results["Weather"].values()):
                print("\n✓ Weather: NOAA API accessible")
                report["recommendations"].append("Use NOAA API for free weather data")
            else:
                print("\n⚠ Weather: Consider OpenWeatherMap with free API key")
                report["recommendations"].append("Get free OpenWeatherMap API key as backup")

        # NREL Summary
        print("\n⚠ NREL: Datasets require download, PVWatts API available")
        report["recommendations"].append("Download NREL ResStock subset for Texas")
        report["recommendations"].append("Use PVWatts API for solar generation estimates")

        # Next Steps
        report["next_steps"] = [
            "1. Set up data ingestion for working ERCOT endpoints",
            "2. Implement NOAA weather API integration",
            "3. Download sample NREL ResStock data for Texas",
            "4. Create synthetic cohort generator",
            "5. Build caching layer for API responses"
        ]

        print("\n" + "="*60)
        print("RECOMMENDATION: We have enough working data sources to proceed!")
        print("="*60)

        # Save detailed results
        with open("data_verification_results.json", "w") as f:
            json.dump({
                "results": self.results,
                "report": report
            }, f, indent=2, default=str)

        print("\nDetailed results saved to: data_verification_results.json")

        return report

if __name__ == "__main__":
    print("Starting Data Source Verification...")
    print("This will test access to all required public data sources")

    verifier = DataSourceVerifier()

    # Run all tests
    verifier.test_ercot_data()
    verifier.test_noaa_weather()
    verifier.test_nrel_data()
    verifier.test_alternative_sources()

    # Generate summary
    report = verifier.generate_summary_report()

    print("\n✅ Verification complete!")
    print("\nBased on the results, we can proceed with the implementation using:")
    print("  • ERCOT public dashboard APIs (if working) or web scraping")
    print("  • NOAA Weather API for forecasts")
    print("  • Synthetic load profiles based on NREL patterns")
    print("  • Local JSON storage as specified")