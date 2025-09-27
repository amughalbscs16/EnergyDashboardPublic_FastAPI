# ERCOT Energy Dashboard - Real-Time Texas Grid Analytics

A comprehensive real-time energy dashboard for monitoring the Texas electricity grid through ERCOT (Electric Reliability Council of Texas) public APIs. This application provides live visualization of energy market data, generation mix, pricing, and grid conditions.

## 🌟 Features

### Real-Time Market Data
- **Live Grid Monitoring**: Current demand, capacity, and reserves
- **Energy Pricing**: Real-time and day-ahead market prices with spread analysis
- **Supply & Demand**: 24-hour forecasting with utilization metrics
- **Physical Responsive Capability (PRC)**: Current and historical PRC values

### Generation Analytics
- **Fuel Mix Visualization**: Real-time breakdown by source (Solar, Wind, Gas, Nuclear, Coal)
- **Renewable Integration**: Solar and wind production tracking
- **Generation Outages**: Planned vs unplanned outage monitoring
- **Capacity Analysis**: Dispatchable vs renewable generation status

### Interactive Visualizations
- **Dynamic Charts**: Powered by Chart.js with real-time updates
- **Multi-Tab Interface**: Organized sections for different data categories
- **Responsive Design**: Modern UI with gradient aesthetics
- **Auto-Refresh**: Live data updates every few seconds

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- ERCOT API credentials ([Get them here](https://www.ercot.com/services/rq/public/public-api))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/amughalbscs16/EnergyDashboardRealDataPublic.git
cd EnergyDashboardRealDataPublic
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API credentials**
```bash
cd ercot_explorer
cp .env.example .env
# Edit .env file with your ERCOT credentials
```

4. **Start the backend API server**
```bash
python backend_simple.py
# Server runs on http://localhost:8000
```

5. **Start the frontend server** (in a new terminal)
```bash
python -m http.server 8080
# Dashboard available at http://localhost:8080
```

6. **Access the dashboard**
Open your browser and navigate to: `http://localhost:8080/dashboard.html`

## 📋 Configuration

### Environment Variables (.env)
Create a `.env` file in the `ercot_explorer` directory with:

```env
# ERCOT API Configuration
ERCOT_USERNAME=your-email@example.com
ERCOT_PASSWORD=your-password
ERCOT_SUBSCRIPTION_KEY=your-subscription-key
ERCOT_AUTH_URL=https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=8080
```

## 📁 Project Structure

```
EnergyDashboardRealDataPublic/
├── ercot_explorer/
│   ├── dashboard.html           # Main dashboard interface
│   ├── backend_simple.py        # FastAPI backend server
│   ├── test_all_endpoints.html  # API endpoint testing utility
│   ├── test_connection.html     # Connection testing tool
│   ├── test_energy_prices.html  # Energy pricing test interface
│   ├── .env                     # Your credentials (not in repo)
│   └── .env.example            # Template for environment variables
├── requirements.txt            # Python dependencies
├── README.md                  # Project documentation
├── .gitignore                # Git ignore rules
└── CLAUDE.md                 # AI assistant guidelines
```

## 🔌 API Endpoints

### Real-Time Data
- `GET /realtime/supply-demand` - Current grid supply and demand metrics
- `GET /realtime/fuel-mix` - Real-time generation by fuel type

### Public Data
- `GET /public/generation-outages` - Current power plant outages
- `GET /public/daily-prc` - Physical Responsive Capability data
- `GET /public/solar-power-production` - Solar generation data
- `GET /public/wind-power-production` - Wind generation data

### Additional Endpoints
- `GET /dr-data` - Demand response data
- `GET /der-data` - Distributed energy resources data
- `GET /endpoints` - List all available endpoints
- `GET /test-all` - Test all API endpoints

## 📊 Dashboard Features

### Supply & Demand Tab
- Real-time grid load (MW)
- Available capacity and reserves
- 24-hour demand forecast
- Utilization percentage

### Generation Tab
- Fuel mix pie chart
- Renewable vs conventional breakdown
- Real-time generation by source
- Trend analysis over 24 hours

### Outages Tab
- Current outage summary
- Planned vs unplanned analysis
- Dispatchable vs renewable impacts
- Historical outage trends

### PRC Tab
- Current PRC value and status
- Historical PRC trends
- Daily and hourly patterns
- Capacity adequacy indicators

### Energy Pricing Tab
- Real-time LMP prices
- Day-ahead market prices
- Price spreads and volatility
- Fuel-based marginal costs

## 🛠️ Technologies Used

### Backend
- **FastAPI** - High-performance Python web framework
- **HTTPX** - Async HTTP client for API calls
- **Python-dotenv** - Environment variable management
- **Uvicorn** - ASGI server for FastAPI

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **Chart.js** - Interactive data visualizations
- **HTML5/CSS3** - Modern web standards
- **Date-fns** - Date formatting utilities

### APIs
- **ERCOT Public API** - Official Texas grid data source
- **OAuth2** - Secure authentication flow

## 🔒 Security

- API credentials stored in `.env` file (excluded from version control)
- CORS configured for localhost development
- Token refresh mechanism for continuous operation
- No sensitive data logged or exposed

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- ERCOT for providing public API access
- Chart.js team for the visualization library
- FastAPI community for the excellent framework

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

## 🔗 Links

- **Repository**: [https://github.com/amughalbscs16/EnergyDashboardRealDataPublic](https://github.com/amughalbscs16/EnergyDashboardRealDataPublic)
- **ERCOT API Documentation**: [https://www.ercot.com/services/rq/public/public-api](https://www.ercot.com/services/rq/public/public-api)
- **Live Demo**: Deploy to your preferred hosting service

---

**Note**: This dashboard uses real-time data from ERCOT's public API. Data accuracy and availability depend on ERCOT's services.