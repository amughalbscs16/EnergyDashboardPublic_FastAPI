"""Main application entry point"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.routers import ercot, weather, cohorts, agents, plans, der, regions
from app.websocket_manager import manager
from app.services.real_ercot_service import RealERCOTService
from app.services.real_weather_service import RealWeatherService

# Create FastAPI app
app = FastAPI(
    title="Utility Portal API",
    description="Real-time utility data and demand response management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ercot.router, prefix="/api/ercot", tags=["ERCOT"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(cohorts.router, prefix="/api/cohorts", tags=["Cohorts"])
app.include_router(agents.router, prefix="/api/agent", tags=["Agent"])
app.include_router(plans.router, prefix="/api/plans", tags=["Plans"])
app.include_router(der.router, prefix="/api/der", tags=["DER"])
app.include_router(regions.router, prefix="/api/regions", tags=["Regions"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Utility Portal API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "ercot": "/api/ercot",
            "weather": "/api/weather",
            "cohorts": "/api/cohorts",
            "agent": "/api/agent",
            "plans": "/api/plans",
            "der": "/api/der",
            "regions": "/api/regions"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)

    # Start broadcasting if not already running
    if not manager.is_broadcasting:
        asyncio.create_task(manager.start_broadcasting(get_realtime_data))

    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back or handle commands
            await manager.send_personal_message(f"Received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        if not manager.active_connections:
            manager.stop_broadcasting()

async def get_realtime_data():
    """Get real-time data for WebSocket broadcast"""
    ercot_service = RealERCOTService()
    weather_service = RealWeatherService()

    # Get current data
    ercot_data = await ercot_service.get_current_conditions()
    weather_data = await weather_service.get_weather("78701")

    return {
        "type": "realtime_update",
        "ercot": {
            "load_mw": ercot_data.get("system_load_mw"),
            "price": ercot_data.get("price_per_mwh"),
            "reserves": ercot_data.get("operating_reserves_mw")
        },
        "weather": {
            "temperature": weather_data.get("temperature_f"),
            "conditions": weather_data.get("conditions")
        }
    }

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8002))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    print(f"Starting Utility Portal API on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"ERCOT API configured: {bool(os.getenv('ERCOT_PUBLIC_API_KEY'))}")
    print(f"ESR API configured: {bool(os.getenv('ERCOT_ESR_API_KEY'))}")

    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )