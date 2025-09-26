# Utility HITL Portal Implementation Plan

## Project Overview
A utility-facing demand response (DR) coordination portal using Texas ERCOT data, weather forecasts, and synthetic load profiles to demonstrate grid management capabilities with human-in-the-loop approval.

## Tech Stack Decision Points

### Backend Options
- **FastAPI (Python)** - Recommended for data science integration
  - ✅ Better for ERCOT API integration
  - ✅ Native pandas/numpy for load profile analysis
  - ✅ Easy async data fetching
  - ✅ Better ML/AI library ecosystem

- **Node.js (Express/Fastify)**
  - ✅ Single language with frontend
  - ✅ Good for real-time updates (WebSockets)
  - ❌ Less mature data science libraries

### Frontend
- **Next.js + TypeScript** - Production ready
- **Tailwind CSS** - Rapid UI development
- **Recharts/Tremor** - Data visualization

### Storage
- **Local JSON files** in `/data` folder for MVP
- **SQLite** for structured queries (optional upgrade)
- **Directory structure**:
  ```
  /data
    /ercot        # Market data snapshots
    /weather      # NOAA forecasts
    /cohorts      # Customer segments
    /plans        # DR plans and results
    /cache        # API response cache
  ```

## Implementation Checklist

### Sprint 1: Foundation (Week 1)

#### Project Setup
- [ ] Initialize project structure
- [ ] Set up Git repository
- [ ] Create Docker Compose for local development
- [ ] Configure environment variables
- [ ] Set up logging system

#### Backend Core
- [ ] FastAPI app initialization
- [ ] CORS configuration
- [ ] Error handling middleware
- [ ] JSON file storage utilities
- [ ] Data validation with Pydantic models

#### Data Models
- [ ] ERCOT snapshot schema
- [ ] Weather data schema
- [ ] Customer cohort schema
- [ ] DR plan schema
- [ ] Signal log schema

#### External Data Integration
- [ ] ERCOT API client (or web scraper)
  - [ ] Real-time load data
  - [ ] Price signals
  - [ ] Generation status
- [ ] NOAA weather API client
  - [ ] Hourly forecasts by ZIP
  - [ ] Temperature, cloud cover
- [ ] Data caching layer (1-hour TTL)
- [ ] Background job scheduler (APScheduler)

#### Synthetic Data Generation
- [ ] NREL EULP profile processor
- [ ] Cohort builder logic
  - [ ] Residential EV owners
  - [ ] Residential with solar/battery
  - [ ] Small commercial HVAC
- [ ] Flexibility calculations per segment

### Sprint 2: Core Features (Week 2)

#### API Endpoints
- [ ] GET /api/v1/context/ercot/current
- [ ] GET /api/v1/context/weather/{zip}
- [ ] GET /api/v1/cohorts
- [ ] POST /api/v1/plan/propose
- [ ] POST /api/v1/plan/{id}/approve
- [ ] GET /api/v1/plan/{id}/status
- [ ] GET /api/v1/plans/history

#### Agent Planning Engine
- [ ] Load forecast analysis
- [ ] Peak detection algorithm
- [ ] DR window optimization
  - [ ] Cost minimization strategy
  - [ ] Reliability strategy
  - [ ] Balanced approach
- [ ] MW relief calculations
- [ ] Acceptance prediction model
- [ ] Constraint validation
  - [ ] Max events per week
  - [ ] Customer comfort limits
  - [ ] Notice time requirements

#### Signal Emulator
- [ ] OpenADR message formatter
- [ ] Simulated endpoint responses
- [ ] Acceptance probability by cohort
- [ ] MW realization calculator

### Sprint 3: Frontend UI (Week 3)

#### Layout & Navigation
- [ ] App shell with sidebar
- [ ] Responsive grid layout
- [ ] Dark/light mode toggle

#### Dashboard Components
- [ ] Situation Overview
  - [ ] ERCOT load gauge
  - [ ] Price spike indicator
  - [ ] Weather stress card
  - [ ] Active alerts
- [ ] Cohort Management Table
  - [ ] Segment details
  - [ ] Available flexibility
  - [ ] Historical performance
- [ ] DR Plan Composer
  - [ ] Time window selector
  - [ ] Strategy picker
  - [ ] Target MW input
  - [ ] Cohort selection

#### Visualization Components
- [ ] 24-hour load forecast chart
- [ ] Price trends graph
- [ ] MW relief timeline
- [ ] Acceptance rate gauges
- [ ] After-action comparison charts

#### HITL Workflow
- [ ] Plan proposal display
- [ ] Approval modal with details
- [ ] Rejection with reason input
- [ ] Action history log

### Sprint 4: Integration & Polish (Week 4)

#### Real-time Updates
- [ ] WebSocket connection for live data
- [ ] Auto-refresh indicators
- [ ] Push notifications for critical events

#### Testing
- [ ] Unit tests for calculations
- [ ] API endpoint tests
- [ ] UI component tests
- [ ] End-to-end workflow tests
- [ ] Load testing with synthetic data

#### Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] User guide for operators
- [ ] Technical architecture diagram
- [ ] Data source attributions

#### Deployment Prep
- [ ] Production Dockerfile
- [ ] Environment configuration
- [ ] Health check endpoints
- [ ] Monitoring setup (basic)
- [ ] Backup/restore for JSON data

## Key Questions to Address

### Data Sources
1. **ERCOT Access**: Do you have an API key, or should we scrape public dashboards?
2. **Weather API**: Use free NOAA API or commercial service (OpenWeatherMap)?
3. **NREL Profiles**: Download specific Texas climate zones or use national averages?

### Feature Priorities
1. **MVP Focus**: Which is more important - realistic data or polished UI?
2. **Agent Complexity**: Simple rule-based or ML-powered predictions?
3. **User Roles**: Single operator view or multiple permission levels?

### Technical Preferences
1. **Python vs Node.js**: Confirm FastAPI for backend?
2. **Database**: Start with JSON files or SQLite from day one?
3. **Deployment**: Local Docker only or cloud-ready (AWS/Azure)?

### Demo Scenarios
1. **Primary Use Case**: Peak shaving or emergency response?
2. **Cohort Size**: 3-5 segments or detailed 10+ segments?
3. **Time Horizon**: Next 24 hours or weekly planning?

## File Structure
```
endeavor-utility-portal/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── agents/
│   │   └── utils/
│   ├── data/
│   │   ├── ercot/
│   │   ├── weather/
│   │   ├── cohorts/
│   │   └── plans/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── types/
│   ├── public/
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## Next Steps
1. Answer the key questions above
2. Choose backend language (Python/FastAPI recommended)
3. Set up initial project structure
4. Begin Sprint 1 tasks

## Success Metrics
- [ ] Demo loads in < 2 seconds
- [ ] Can process 100k synthetic customers
- [ ] DR plan generation < 5 seconds
- [ ] Clear HITL approval workflow
- [ ] Realistic ERCOT data integration
- [ ] Professional utility-grade UI