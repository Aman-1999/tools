# 🎯 Rank Tracker Prototype

A powerful prototype rank tracking tool that checks both **organic** and **Google Maps rankings** using the DataForSEO API with advanced geocoding capabilities.

## ✨ Features

- **🌐 Organic Rankings**: Track top 100 organic search results
- **📍 Maps Rankings**: Track Google Maps/Local Pack results  
- **🎯 Precise Geocoding**: Convert addresses to coordinates using multiple providers
- **📱 Device Targeting**: Desktop and mobile ranking checks
- **🚀 Async Processing**: Fast, concurrent API calls
- **🌍 Multi-Location**: Support for addresses, PIN codes, cities
- **📊 Rich Results**: Detailed ranking data with metadata
- **🔄 Real-time**: Live results via modern web interface

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.8+)
- **SERP API**: DataForSEO (Organic + Maps)
- **Geocoding**: Google Maps API, OpenCage, Nominatim (fallback)
- **Async**: aiohttp for concurrent requests
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Validation**: Pydantic models

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **DataForSEO API account** ([Sign up here](https://dataforseo.com))
3. **Geocoding API key** (Google Maps or OpenCage - optional but recommended)

## 🚀 Quick Setup

### 1. Clone and Setup

```bash
# Clone or download the prototype files
# Navigate to the directory
cd rank-tracker-prototype

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Edit the `.env` file with your API credentials:

```bash
# DataForSEO API Credentials (Required)
DATAFORSEO_LOGIN=your_dataforseo_login
DATAFORSEO_PASSWORD=your_dataforseo_password

# Geocoding API Keys (Optional but recommended)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
OPENCAGE_API_KEY=your_opencage_api_key

# Application Settings
ENVIRONMENT=development
DEBUG=True
DEFAULT_DEPTH=40
```

### 3. Run the Application

```bash
# Method 1: Direct Python
python main.py

# Method 2: Using startup scripts
# Windows:
start.bat
# Linux/Mac:
./start.sh
```

### 4. Access the Interface

- **Web Interface**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Alternative API Docs**: http://127.0.0.1:8000/redoc

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Make sure the server is running first
python main.py

# In another terminal, run tests
python test_api.py
```

## 📱 Web Interface

The prototype includes a modern, responsive web interface that allows you to:

- Enter keywords and locations
- Select device type (desktop/mobile)
- Choose language and results depth
- View real-time ranking results
- See geocoded location data
- Export results

## 🔧 API Endpoints

### Main Endpoints

- `GET /` - Web interface
- `GET /health` - Health check
- `GET /api/status` - API status and connectivity
- `POST /api/check-rankings` - Main ranking check endpoint

### Sample API Request

```bash
curl -X POST "http://127.0.0.1:8000/api/check-rankings" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "pizza restaurant",
    "location": {
      "address": "New York, NY",
      "pincode": "10001"
    },
    "device": "desktop",
    "language_code": "en",
    "depth": 40
  }'
```

## 📊 Response Format

```json
{
  "keyword": "pizza restaurant",
  "location": {
    "address": "New York, NY, 10001",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "city": "New York",
    "country": "United States"
  },
  "device": "desktop",
  "language_code": "en",
  "depth": 40,
  "organic_results": [
    {
      "position": 1,
      "title": "Best Pizza in NYC",
      "description": "...",
      "url": "https://example.com",
      "domain": "example.com"
    }
  ],
  "maps_results": [
    {
      "position": 1,
      "title": "Joe's Pizza",
      "address": "123 Main St, New York, NY",
      "phone": "(555) 123-4567",
      "rating": 4.5,
      "reviews_count": 1250
    }
  ],
  "check_date": "2025-01-01T12:00:00Z",
  "processing_time_seconds": 15.2
}
```

## 🔑 API Keys Setup

### DataForSEO (Required)
1. Sign up at [DataForSEO](https://app.dataforseo.com/register)
2. Get your login credentials from the dashboard
3. Add to `.env` file

### Google Maps Geocoding (Recommended)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Geocoding API
3. Create an API key
4. Add to `.env` file

### OpenCage (Alternative)
1. Sign up at [OpenCage](https://opencagedata.com/users/sign_up)
2. Get your API key
3. Add to `.env` file

## 🚨 Troubleshooting

### Common Issues

**"ModuleNotFoundError"**
```bash
# Make sure virtual environment is activated
pip install -r requirements.txt
```

**"DataForSEO authentication failed"**
- Check your login credentials in `.env`
- Ensure you have active DataForSEO credits

**"Geocoding failed"**
- The system will fallback to free Nominatim
- Add Google Maps or OpenCage API key for better accuracy

**"Port already in use"**
```bash
# Change port in .env file
API_PORT=8001
```

## 📁 File Structure

```
rank-tracker-prototype/
├── main.py                 # Main FastAPI application
├── config.py              # Configuration settings
├── models.py              # Data models
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
├── README.md             # This file
├── test_api.py           # Test suite
├── start.sh              # Linux/Mac startup script
├── start.bat             # Windows startup script
├── services/
│   ├── __init__.py       # Services package
│   ├── dataforseo_client.py  # DataForSEO API client
│   └── geocoding_client.py   # Geocoding client
└── logs/                 # Auto-created log files
```

## 💰 Cost Estimation

**DataForSEO Usage**:
- Organic check: ~$0.002 per request
- Maps check: ~$0.003 per request
- 1000 checks/day ≈ $5/month

**Geocoding** (optional):
- Google Maps: $5 per 1000 requests
- OpenCage: $1 per 1000 requests
- Nominatim: Free (used as fallback)

## 🔮 Future Enhancements

This prototype can be extended with:
- Database storage for historical data
- Multi-client support
- Scheduled ranking checks
- Email/Slack notifications
- Advanced reporting and analytics
- White-label customization
- Grid-based local rank tracking

## 🆘 Support

1. **Check the logs**: Look in the `logs/` directory
2. **Run tests**: Use `python test_api.py`
3. **API docs**: Visit http://127.0.0.1:8000/docs
4. **Debug mode**: Set `DEBUG=True` in `.env`

## 📄 License

This is a prototype for evaluation purposes. Please ensure compliance with all API terms of service.

---

**🚀 Ready to track rankings! Start with `python main.py` and visit http://127.0.0.1:8000**"# tools" 
"# tools" 
