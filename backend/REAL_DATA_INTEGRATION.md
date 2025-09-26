# Real Data Integration Service

This document describes the comprehensive real data integration service that has been implemented for the backend. The service integrates with real-world APIs to provide live ERCOT and weather data with robust fallback mechanisms.

## Overview

The real data integration system provides:
- **ERCOT Data**: Real-time electricity grid data from Texas
- **Weather Data**: Current conditions and forecasts with multiple API sources
- **Smart Fallbacks**: Synthetic data generation when APIs are unavailable
- **Caching**: Intelligent caching to minimize API calls and improve performance
- **Rate Limiting**: Built-in protection against API rate limits

## Architecture

### Services

1. **`real_data_service.py`** - Comprehensive service orchestrating all data sources
2. **`ercot_service.py`** - Enhanced ERCOT-specific data service
3. **`weather_service.py`** - Multi-source weather data service

### Data Flow

```
API Request → Cache Check → Real API Call → Transform Data → Cache Result → Return Response
                ↓                ↓
            Cache Hit        API Failure
                ↓                ↓
            Return Cached    Synthetic Data
```

## API Integration

### ERCOT API

**Source**: `https://apiexplorer.ercot.com/`
**Authentication**: API Key required

**Endpoints Used**:
- `np6-345-cd`: Current system load
- `np6-905-cd`: Real-time market prices
- `np4-737-cd`: Wind generation output
- `np4-745-cd`: Solar generation output
- `np3-566-cd`: Load forecasts

**Data Provided**:
- Current system load (MW)
- Electricity prices ($/MWh)
- Operating reserves
- Renewable generation (wind/solar)
- Load forecasts
- System alerts

### Weather APIs

#### Primary: OpenWeather API
**Source**: `https://openweathermap.org/api`
**Authentication**: API Key required
**Free Tier**: 1000 calls/day, 60 calls/minute

**Features**:
- Current weather conditions
- 5-day/3-hour forecasts
- Multiple data points (temperature, humidity, wind, etc.)

#### Fallback: National Weather Service (NWS)
**Source**: `https://api.weather.gov`
**Authentication**: None required
**Free**: Unlimited use

**Features**:
- Current observations from weather stations
- Hourly forecasts
- Weather alerts and warnings

### Synthetic Data Generation

When real APIs are unavailable, the system generates realistic synthetic data based on:
- **ERCOT**: Historical Texas grid patterns, seasonal variations, time-of-day factors
- **Weather**: Texas climate patterns, seasonal temperatures, realistic variations

## Configuration

### Environment Variables

```env
# ERCOT API Keys
ERCOT_PUBLIC_API_KEY=your_ercot_public_api_key_here
ERCOT_ESR_API_KEY=your_ercot_esr_api_key_here

# OpenWeather API Key
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Cache Settings
ERCOT_CACHE_MINUTES=5
WEATHER_CACHE_MINUTES=30
FORECAST_CACHE_MINUTES=60
```

### Getting API Keys

1. **ERCOT API Keys**:
   - Visit: https://apiexplorer.ercot.com/
   - Create free account
   - Subscribe to Public Reports API
   - Copy API keys to `.env` file

2. **OpenWeather API Key**:
   - Visit: https://openweathermap.org/api
   - Create free account
   - Generate API key
   - Copy to `.env` file

## Usage

### Basic Usage

```python
from app.services.real_data_service import RealDataService

async with RealDataService() as rds:
    # Get ERCOT data
    ercot_data = await rds.get_ercot_current_conditions()

    # Get weather data
    weather_data = await rds.get_weather_data("78701")

    # Get comprehensive data
    all_data = await rds.get_comprehensive_data("78701")
```

### Router Endpoints

**ERCOT Endpoints**:
- `GET /api/ercot/current` - Current system conditions
- `GET /api/ercot/forecast` - Load forecast
- `GET /api/ercot/ancillary-services` - Ancillary services data

**Weather Endpoints**:
- `GET /api/weather/{zip_code}` - Current weather
- `GET /api/weather/{zip_code}/alerts` - Weather alerts
- `GET /api/weather/forecast/{zip_code}` - Weather forecast

## Data Structure

### ERCOT Current Conditions

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "system_load_mw": 45000,
  "capacity_mw": 86000,
  "operating_reserves_mw": 3000,
  "price_per_mwh": 35.50,
  "frequency_hz": 60.0,
  "forecast_peak_mw": 50000,
  "forecast_peak_hour": 16,
  "renewable_output_mw": {
    "wind": 15000,
    "solar": 8000,
    "total": 23000
  },
  "alerts": [],
  "data_source": "ercot_api"
}
```

### Weather Data

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "zip_code": "78701",
  "temperature_f": 75.0,
  "humidity_pct": 60,
  "cloud_cover_pct": 25,
  "wind_speed_mph": 10.5,
  "conditions": "Partly Cloudy",
  "heat_index_f": 78.0,
  "dew_point_f": 65.0,
  "pressure_mb": 1013,
  "visibility_miles": 10.0,
  "forecast_24h": [...],
  "data_source": "openweather"
}
```

## Caching Strategy

### Cache Durations
- **ERCOT Current**: 5 minutes (high frequency updates)
- **ERCOT Forecast**: 60 minutes (updated less frequently)
- **Weather Current**: 30 minutes (moderate frequency)
- **Synthetic Data**: 10 minutes (shorter cache for fallback)

### Cache Implementation
- File-based caching in `data/cache/` directory
- TTL (Time To Live) based expiration
- Automatic cleanup of expired cache files

## Error Handling

### Fallback Hierarchy

1. **Primary API** (ERCOT/OpenWeather)
2. **Secondary API** (NWS for weather)
3. **Cached Data** (if available and recent)
4. **Synthetic Data** (always available)

### Error Types Handled
- Network timeouts
- API rate limiting
- Authentication failures
- Invalid responses
- Service unavailability

## Performance Features

### Rate Limiting
- Built-in rate limiters prevent API quota exhaustion
- Configurable limits per API
- Automatic backoff on rate limit hits

### Async Operations
- All API calls are asynchronous
- Concurrent requests where possible
- Non-blocking fallback mechanisms

### Resource Management
- Proper session management for HTTP clients
- Context managers for resource cleanup
- Memory-efficient data structures

## Testing

### Test Scripts

1. **`test_real_data_services.py`** - Comprehensive service testing
2. **`test_routers_simple.py`** - Router function testing

### Running Tests

```bash
# Test all services
python test_real_data_services.py

# Test router functions
python test_routers_simple.py
```

### Test Coverage
- API integration testing
- Fallback mechanism testing
- Data transformation testing
- Cache functionality testing
- Error handling testing

## Monitoring and Logging

### Log Levels
- **INFO**: Successful API calls and cache hits
- **WARNING**: API failures triggering fallbacks
- **ERROR**: Unexpected errors and exceptions

### Key Metrics
- API response times
- Cache hit/miss ratios
- Fallback usage frequency
- Error rates by service

## Dependencies

### Required Packages
```
aiohttp>=3.8.0
requests>=2.28.0
fastapi>=0.68.0
```

### Installation
```bash
pip install -r requirements.txt
```

## Deployment Considerations

### Environment Setup
1. Configure API keys in production environment
2. Set appropriate cache directories with write permissions
3. Configure logging levels for production
4. Set up monitoring for API usage and errors

### Scaling
- Services are stateless and can be horizontally scaled
- Cache can be moved to Redis for multi-instance deployments
- Rate limiters can be centralized for coordinated limiting

### Security
- API keys should be stored securely (environment variables, secrets management)
- Implement request validation and sanitization
- Consider API key rotation policies

## Troubleshooting

### Common Issues

1. **API Keys Not Working**
   - Verify keys are correctly set in `.env`
   - Check API subscription status
   - Verify endpoint permissions

2. **High API Usage**
   - Check cache hit rates
   - Verify cache TTL settings
   - Monitor for unnecessary duplicate requests

3. **Synthetic Data Always Used**
   - Check API key configuration
   - Verify network connectivity
   - Review API service status

### Debug Mode
Set `DEBUG=True` in `.env` for detailed logging and error information.

## Future Enhancements

### Potential Additions
- Additional ERCOT endpoints (outages, congestion)
- Weather radar/satellite integration
- Historical data storage and analytics
- Machine learning for improved synthetic data
- Real-time WebSocket connections
- Multi-region weather support

### Performance Improvements
- Redis caching
- Database storage for historical trends
- GraphQL API interface
- Batch request optimization
- Predictive prefetching

## Support

For issues or questions about the real data integration service:
1. Check the test scripts for validation
2. Review logs for error details
3. Verify API key configuration
4. Consult API provider documentation