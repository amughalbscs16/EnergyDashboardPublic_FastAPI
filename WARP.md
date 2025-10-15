# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Common Development Commands

### Backend (FastAPI)
```bash
# Start the backend server
cd ercot_explorer
python backend_simple.py
# Server runs on http://localhost:8000

# Install dependencies
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# Edit .env with your ERCOT and OpenAI API credentials
```

### Frontend (Static HTML/JavaScript)
```bash
# Start frontend development server
cd ercot_explorer
python -m http.server 8080
# Frontend available at http://localhost:8080/dashboard.html

# Test pages available at:
# http://localhost:8080/test_connection.html
# http://localhost:8080/test_all_endpoints.html
# http://localhost:8080/test_energy_prices.html
# http://localhost:8080/test_api_status.html
```

### Testing and Development
```bash
# Test ERCOT API authentication
curl http://localhost:8000/test-token

# Test all ERCOT endpoints
curl http://localhost:8000/test-all

# Refresh authentication token
curl http://localhost:8000/refresh-token

# View API documentation
# Visit http://localhost:8000/docs (FastAPI auto-generated docs)
```

## Architecture Overview

### High-Level Structure
This is a **real-time energy dashboard** for monitoring Texas electricity grid data via ERCOT APIs. The application follows a **client-server architecture** with:

- **Backend**: FastAPI Python server (`backend_simple.py`) that handles ERCOT API integration and AI assistant functionality
- **Frontend**: Single-page application (`dashboard.html`) with vanilla JavaScript and Chart.js visualizations
- **Data Flow**: Backend fetches real-time data from ERCOT APIs → Frontend displays in interactive charts and metrics
- **AI Integration**: GPT-5-nano powered assistant with context from dashboard data

### Key Components

#### Backend API (`backend_simple.py`)
- **ERCOT Integration**: OAuth authentication with token caching and automatic refresh
- **Data Endpoints**: 15+ predefined ERCOT endpoints covering DR (Demand Response), DER (Distributed Energy Resources), and Grid operations
- **AI Assistant**: OpenAI integration with dashboard context awareness and cost tracking
- **Real-time Data**: Public ERCOT dashboard endpoints (supply-demand, fuel-mix, outages, etc.)

#### Frontend Dashboard (`dashboard.html`)
- **Multi-tab Interface**: 11 specialized tabs (Overview, Real-Time Grid, Generation, Market Data, DER Resources, etc.)
- **Chart.js Integration**: Interactive time-series charts, pie charts, and real-time data visualization
- **AI Chat Interface**: Context-aware assistant that can analyze data from any tab
- **Responsive Design**: Desktop and mobile optimized with gradient styling

### Data Sources and Flow

#### ERCOT API Integration
- **Authentication**: OAuth 2.0 with B2C flow, token caching with 5-minute buffer
- **Primary APIs**: Official ERCOT Public API with subscription key
- **Public Endpoints**: Direct access to ERCOT dashboard JSON feeds (no auth required)
- **Data Categories**:
  - **DR (Demand Response)**: Load forecasts, settlement prices, system conditions
  - **DER (Distributed Energy Resources)**: Solar/wind production, generation summaries
  - **Grid Operations**: Shadow prices, ancillary services, outages

#### Frontend Data Processing
- **Auto-refresh**: 5-minute intervals for real-time accuracy
- **Chart Data**: Processed for Chart.js consumption with time-series formatting
- **Tab Context**: Each tab maintains its own data state for AI assistant context
- **Error Handling**: Graceful degradation when APIs are unavailable

### Environment Configuration

#### Required API Credentials
```bash
# ERCOT API (required for authenticated endpoints)
ERCOT_USERNAME=your-email@example.com
ERCOT_PASSWORD=your-password
ERCOT_SUBSCRIPTION_KEY=your-subscription-key

# OpenAI API (required for AI assistant)
OPENAI_API_KEY=sk-proj-your-openai-key
```

#### ERCOT API Registration
- Register at: https://www.ercot.com/services/rq/public/public-api
- Subscription required for authenticated endpoints
- Public dashboard endpoints work without authentication

### AI Assistant Integration

#### GPT-5-nano Implementation
- **Model**: Uses OpenAI Responses API with gpt-5-nano model
- **Context**: Full dashboard data passed to AI for comprehensive analysis
- **Cost Tracking**: Detailed token usage and cost monitoring in `ai_cost_tracking.json`
- **Session History**: Conversation persistence with 1000-session limit

#### AI Context Structure
- Current tab data (including chart datasets and labels)
- Grid metrics (demand, capacity, prices, outages)
- Additional selected data sources from other tabs
- Real-time timestamps and conditions

### Development Patterns

#### Backend Patterns
- **Error Handling**: Comprehensive try-catch with HTTP status codes
- **Token Management**: Automatic refresh with failure counting
- **Data Processing**: Artifact following for ERCOT metadata responses
- **CORS**: Fully open for development (restrict in production)

#### Frontend Patterns
- **Tab Management**: Show/hide with fadeIn animations
- **Chart Lifecycle**: Destroy and recreate charts on data updates
- **Data Fetching**: Promise-based with error handling and loading states
- **Context Building**: Collect data from multiple sources for AI assistant

### File Structure Context
```
ercot_explorer/          # Main application directory
├── backend_simple.py    # FastAPI server with ERCOT + AI integration
├── dashboard.html       # Main dashboard interface
├── test_*.html         # Development and testing pages
├── .env.example        # Environment configuration template
└── ai_cost_tracking.json  # AI usage cost tracking (generated)

images/                 # Screenshots for README
requirements.txt        # Python dependencies
temp_market_data.json   # Temporary data cache (generated)
.claude/               # Claude-specific configuration
└── settings.local.json # Claude permissions for development
```

## Key Technical Considerations

### Authentication & API Limits
- ERCOT tokens expire after 1 hour (55-minute cache with 5-minute buffer)
- Failed request counting triggers token refresh
- Rate limiting may apply to ERCOT APIs (not documented in code)

### Data Refresh Strategy
- Frontend auto-refreshes every 5 minutes
- Manual refresh buttons available on each tab
- Backend caches tokens but not data (always fetches fresh)

### AI Assistant Considerations
- GPT-5-nano pricing: $0.05/1M input tokens, $0.40/1M output tokens
- Context can be very large with full chart data
- Session history saved locally for cost analysis

### Production Readiness Notes
- CORS configured for development (* origins) - needs restriction for production
- No HTTPS enforcement in development setup
- Environment variables contain sensitive credentials
- No database persistence - all data is real-time or file-based