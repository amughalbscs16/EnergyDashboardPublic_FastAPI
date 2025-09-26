# Utility HITL Portal - Texas Grid Demand Response System

A demonstration portal for utility operators to coordinate demand response (DR) events on the Texas ERCOT grid using Human-in-the-Loop (HITL) approval workflows.

## Features

- **Real-time Grid Monitoring**: Displays ERCOT system load, prices, and reserves
- **Weather Integration**: Shows temperature and conditions affecting demand
- **Customer Cohort Management**: 6 pre-configured segments with ~13,000 accounts
- **AI-Powered Planning**: Agent proposes optimal DR strategies
- **HITL Approval**: Operators review and approve before dispatch
- **OpenADR-style Signals**: Simulated endpoint responses

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
# Start both backend and frontend
docker-compose up

# Access the application
# Frontend: http://localhost:3001
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Installation

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
python -m uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run the frontend
npm run dev
```

Access the application at http://localhost:3001

## Architecture

```
utility-portal/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── agents/   # DR planning intelligence
│   │   ├── models/   # Data models
│   │   ├── routers/  # API endpoints
│   │   └── services/ # Data generation
│   └── data/         # JSON storage
│       ├── ercot/    # Grid data
│       ├── weather/  # Weather cache
│       ├── cohorts/  # Customer segments
│       ├── plans/    # DR plans
│       └── signals/  # OpenADR signals
└── frontend/         # Next.js UI
    └── src/
        └── app/      # Dashboard components
```

## Usage Guide

### 1. View System Status
- Monitor current grid load (GW)
- Check electricity prices ($/MWh)
- View temperature and weather
- See 24-hour load forecast

### 2. Select Customer Cohorts
Available segments with total flexibility:
- **Residential EV** (Austin): 18.0 MW
- **Residential Solar+Battery** (Houston): 6.0 MW
- **Residential Standard** (Dallas): 21.3 MW
- **Commercial HVAC** (Austin South): 11.3 MW
- **Commercial Lighting** (Houston): 4.8 MW
- **Industrial Manufacturing** (Dallas): 42.5 MW

Total: **103.9 MW** flexible capacity

### 3. Generate DR Plan
1. Select cohorts (or leave blank for auto-selection)
2. Choose strategy:
   - **Balanced**: Optimize across all factors
   - **Cost Minimize**: Target high-price periods
   - **Reliability**: Enhance grid stability
   - **Emergency**: Maximum reduction
3. Click "Generate Plan"

### 4. Review & Approve
- Review target MW reduction
- Check predicted response
- Verify confidence score
- Click "Approve & Send" to dispatch signals

### 5. Monitor Results
- View signal status at `/api/v1/signals`
- Check plan execution at `/api/v1/plans/{plan_id}/status`

## API Endpoints

### ERCOT Data
- `GET /api/v1/context/ercot/current` - Current system conditions
- `GET /api/v1/context/ercot/forecast` - 24-hour forecast

### Weather
- `GET /api/v1/context/weather/{zip}` - Weather by ZIP code

### Cohorts
- `GET /api/v1/cohorts` - List all cohorts
- `GET /api/v1/cohorts/{id}/flexibility` - Cohort flexibility

### DR Plans
- `POST /api/v1/plans/propose` - Create new plan
- `POST /api/v1/plans/{id}/approve` - Approve plan
- `GET /api/v1/plans/{id}/status` - Plan status

Full API documentation: http://localhost:8000/docs

## Data Sources

- **ERCOT**: Synthetic data based on typical Texas grid patterns
- **Weather**: Synthetic Texas summer conditions
- **Load Profiles**: Based on NREL research patterns
- **Cohorts**: Realistic customer segments for Texas cities

## Demo Scenario

For USCIS demonstration:

"This portal helps Texas utilities manage electricity demand during peak periods. Using public grid data and weather forecasts, an AI agent identifies when the grid is stressed and recommends asking certain customer groups to reduce usage. A human operator reviews and approves these recommendations before any action is taken. The system simulates customer responses to show potential grid relief of 50-100 MW, equivalent to avoiding a small power plant startup. This supports grid reliability and reduces costs for all Texans."

## Technical Stack

- **Backend**: Python FastAPI, Pydantic, APScheduler
- **Frontend**: Next.js, TypeScript, Tailwind CSS, Tremor
- **Storage**: Local JSON files (easily upgradeable to PostgreSQL)
- **Charts**: Recharts
- **Icons**: Lucide React

## Development

### Add New Cohorts
Edit `backend/app/services/data_generator.py`

### Modify Planning Logic
Edit `backend/app/agents/planner.py`

### Update UI Components
Edit `frontend/src/app/page.tsx`

## Future Enhancements

- Real ERCOT API integration (requires registration)
- NOAA Weather API integration (working, ready to enable)
- PostgreSQL for production storage
- WebSocket for real-time updates
- Historical analytics dashboard
- Multi-user role management

## License

MIT

## Support

For questions or issues, please open a GitHub issue.