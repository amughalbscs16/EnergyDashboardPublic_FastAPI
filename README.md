# ERCOT Energy Dashboard

## Overview
Real-time energy market dashboard for ERCOT (Electric Reliability Council of Texas) providing comprehensive visualization of Texas electricity grid data, pricing, and market conditions.

## Features

- **Real-Time Energy Pricing** - Live market prices, day-ahead pricing, and settlement point analysis
- **Supply & Demand Monitoring** - Current grid load, available capacity, and reserve margins
- **Generation Mix Tracking** - Real-time fuel mix including solar, wind, gas, nuclear, and coal
- **Outage Monitoring** - Power plant outage tracking with planned vs unplanned analysis
- **Market Analytics** - Physical Responsive Capability (PRC) trends and market conditions
- **Interactive Visualizations** - Dynamic charts powered by Chart.js

## Quick Start

### Prerequisites
- Python 3.8+

### Installation

1. Clone the repository
```bash
git clone https://github.com/amughalbscs16/EnergyDashboardRealDataPublic.git
cd EnergyDashboardRealDataPublic
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
cd ercot_explorer
cp .env.example .env
# Edit .env with your ERCOT API credentials
```

4. Start the backend API server
```bash
cd ercot_explorer
python backend_simple.py
```

5. Open the dashboard
```bash
# Open ercot_explorer/dashboard.html in your browser
# Or visit http://localhost:8080 if using the built-in server
```

## Configuration

Create `.env` file in `ercot_explorer/` directory with your ERCOT API credentials:
```
ERCOT_USERNAME=your-email@example.com
ERCOT_PASSWORD=your-password
ERCOT_SUBSCRIPTION_KEY=your-subscription-key
ERCOT_AUTH_URL=https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=8080
```

Get your ERCOT API credentials at: https://www.ercot.com/services/rq/public/public-api

## Project Structure

```
├── ercot_explorer/
│   ├── dashboard.html           # Main dashboard interface
│   ├── backend_simple.py        # FastAPI backend with ERCOT API integration
│   ├── test_all_endpoints.html  # API endpoint testing utility
│   ├── test_connection.html     # Connection testing tool
│   ├── test_energy_prices.html  # Energy pricing test interface
│   ├── .env                     # Your API credentials (not in repo)
│   └── .env.example             # Template for environment variables
├── requirements.txt             # Python dependencies
├── README.md                   # This file
└── .gitignore                 # Git ignore rules
```

## API Endpoints

The backend provides these endpoints for the dashboard:

- `GET /realtime/supply-demand` - Current grid supply and demand
- `GET /realtime/fuel-mix` - Real-time generation by fuel type
- `GET /public/generation-outages` - Current power plant outages
- `GET /public/daily-prc` - Physical Responsive Capability data
- `GET /public/solar-power-production` - Solar generation data
- `GET /public/wind-power-production` - Wind generation data

## Technologies Used

- **Backend**: FastAPI, Python, HTTPX for API calls
- **Frontend**: Vanilla JavaScript, Chart.js for visualizations
- **Styling**: Modern CSS with gradients and animations
- **APIs**: ERCOT Public API for real-time Texas grid data

## License

MIT License