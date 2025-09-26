"""Texas region configuration for major cities"""

from typing import Dict, List

# Major Texas cities with ZIP codes
TEXAS_REGIONS = {
    "austin": {
        "name": "Austin",
        "zip_codes": ["78701", "78702", "78703", "78704", "78705"],
        "primary_zip": "78701",
        "coordinates": {"lat": 30.2672, "lon": -97.7431},
        "population": 964254,
        "metro_area": "Austin-Round Rock-Georgetown"
    },
    "dallas": {
        "name": "Dallas",
        "zip_codes": ["75201", "75202", "75203", "75204", "75205"],
        "primary_zip": "75201",
        "coordinates": {"lat": 32.7767, "lon": -96.7970},
        "population": 1304379,
        "metro_area": "Dallas-Fort Worth-Arlington"
    },
    "houston": {
        "name": "Houston",
        "zip_codes": ["77001", "77002", "77003", "77004", "77005"],
        "primary_zip": "77002",
        "coordinates": {"lat": 29.7604, "lon": -95.3698},
        "population": 2320268,
        "metro_area": "Houston-The Woodlands-Sugar Land"
    },
    "san_antonio": {
        "name": "San Antonio",
        "zip_codes": ["78201", "78202", "78203", "78204", "78205"],
        "primary_zip": "78202",
        "coordinates": {"lat": 29.4241, "lon": -98.4936},
        "population": 1547253,
        "metro_area": "San Antonio-New Braunfels"
    }
}

def get_region_by_name(region_name: str) -> Dict:
    """Get region data by name"""
    return TEXAS_REGIONS.get(region_name.lower())

def get_all_regions() -> List[str]:
    """Get list of all available regions"""
    return list(TEXAS_REGIONS.keys())

def get_region_zip_codes() -> Dict[str, str]:
    """Get mapping of ZIP codes to region names"""
    mapping = {}
    for region_key, region_data in TEXAS_REGIONS.items():
        for zip_code in region_data["zip_codes"]:
            mapping[zip_code] = region_key
    return mapping