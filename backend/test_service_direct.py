#!/usr/bin/env python3
"""Test RealERCOTService directly"""

import asyncio
import sys
import os
sys.path.append('.')

from app.services.real_ercot_service import RealERCOTService

async def test_service():
    """Test the actual service used by the API"""
    print("Testing RealERCOTService directly...")
    print("=" * 50)

    service = RealERCOTService()

    result = await service.get_current_conditions()

    print(f"Result keys: {list(result.keys())}")
    print(f"Data source: {result.get('data_source')}")
    print(f"API status: {result.get('api_status')}")

    if 'system_load_mw' in result:
        print(f"System load: {result.get('system_load_mw')} MW")
        print(f"System capacity: {result.get('system_capacity_mw')} MW")
        print("SUCCESS: Service returning real data!")
    else:
        print("Service not returning real data")
        print(f"Full result: {result}")

if __name__ == "__main__":
    asyncio.run(test_service())