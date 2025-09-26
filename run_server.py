#!/usr/bin/env python3
"""Run the new real data API server"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Set environment variables
os.environ["ERCOT_PUBLIC_API_KEY"] = "YOUR_SUBSCRIPTION_KEY_HERE"
os.environ["ERCOT_ESR_API_KEY"] = "0dd522cdfdd24a09941bcb71af5d3596"

# Import and run
from backend.main import app
import uvicorn

if __name__ == "__main__":
    print("Starting Real Data API Server on port 8002")
    print("=" * 50)
    print("ERCOT API Keys: Configured")
    print("Weather API: NOAA (no key required)")
    print("Cohort Data: Real Texas utility segments")
    print("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=8002, reload=False)