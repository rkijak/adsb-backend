# ADS-B Aircraft Tracking Backend

A Flask-based REST API backend for real-time aircraft tracking using ADS-B data from the OpenSky Network. This system enables aircraft monitoring, flight data retrieval, and integrates with Mistral AI for natural language queries.

## 🚀 Features

- **Real-time Aircraft Tracking**: Query aircraft by geographic location with customizable radius
- **Flight History**: Retrieve historical flight data for specific aircraft
- **Airport Operations**: Get arrivals and departures for any airport
- **Distance Calculator**: Calculate great circle distances between coordinates
- **Aircraft Details**: Comprehensive aircraft information including position, velocity, altitude, and more
- **Mistral AI Integration**: Natural language interface for querying aircraft data
- **RESTful API**: Clean, well-documented API endpoints

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenSky Network API access (optional: credentials for higher rate limits)
- Mistral AI API key (for AI agent integration)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/rkijak/adsb-backend.git
cd adsb-backend
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5001

# OpenSky Network Credentials (Optional - improves rate limits)
OPENSKY_USERNAME=your_username
OPENSKY_PASSWORD=your_password

# Mistral AI Configuration
MISTRAL_API_KEY=your_mistral_api_key_here
```

> **Note**: OpenSky credentials are optional but recommended for better rate limits. Anonymous access is limited to 10 requests per 10 seconds.

## 🎯 Usage

### Starting the Backend Server

```bash
python3 app.py
```

The server will start on `http://127.0.0.1:5001`

### API Endpoints

#### 1. Get Aircraft by Area
```http
GET /api/aircraft/area?lat=37.7749&lon=-122.4194&radius=50
```

**Parameters:**
- `lat` (float): Latitude in decimal degrees
- `lon` (float): Longitude in decimal degrees
- `radius` (float): Search radius in nautical miles

**Example Response:**
```json
{
  "aircraft_count": 15,
  "area": {
    "center": {"lat": 37.7749, "lon": -122.4194},
    "radius_nm": 50
  },
  "aircraft": [
    {
      "icao24": "a12345",
      "callsign": "UAL123",
      "origin_country": "United States",
      "latitude": 37.7850,
      "longitude": -122.4100,
      "baro_altitude": 3048.0,
      "velocity": 250.5,
      "true_track": 45.0,
      "vertical_rate": 0.0,
      "on_ground": false,
      "distance_nm": 5.2
    }
  ]
}
```

#### 2. Get Aircraft Details
```http
GET /api/aircraft/a12345
```

**Parameters:**
- `icao24` (string): Aircraft ICAO24 transponder address

#### 3. Get Flight History
```http
GET /api/flights/a12345?begin=1699660800&end=1699747200
```

**Parameters:**
- `icao24` (string): Aircraft ICAO24 address
- `begin` (int): Start time (Unix timestamp)
- `end` (int): End time (Unix timestamp)

#### 4. Get Airport Arrivals/Departures
```http
GET /api/airport/KJFK?begin=1699660800&end=1699747200
```

**Parameters:**
- `icao` (string): Airport ICAO code (e.g., KJFK, EGLL)
- `begin` (int): Start time (Unix timestamp)
- `end` (int): End time (Unix timestamp)

#### 5. Calculate Distance
```http
GET /api/distance?lat1=37.7749&lon1=-122.4194&lat2=40.7128&lon2=-74.0060
```

**Parameters:**
- `lat1`, `lon1` (float): First coordinate
- `lat2`, `lon2` (float): Second coordinate

**Example Response:**
```json
{
  "distance_km": 4129.2,
  "distance_nm": 2229.5,
  "distance_miles": 2565.6
}
```

## 🤖 Mistral AI Integration

### Running the AI Agent

```bash
python3 mistral_agent.py
```

### Example Queries

```
> Show me aircraft near San Francisco within 50 nautical miles
> What flights are arriving at JFK airport?
> Calculate distance from New York to London
> Get details for aircraft with callsign UAL123
```

The AI agent automatically calls the appropriate API endpoints and formats responses in natural language.

## 📁 Project Structure

```
adsb-backend/
├── app.py                 # Flask application and API routes
├── config.py              # Configuration and constants
├── opensky_service.py     # OpenSky Network API integration
├── utils.py               # Helper functions (distance calc, conversions)
├── mistral_agent.py       # Mistral AI agent integration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── .gitignore            # Git ignore rules
```

## 🔧 Configuration

### Flask Settings
- `FLASK_PORT`: Server port (default: 5001)
- `FLASK_DEBUG`: Enable debug mode
- `FLASK_ENV`: Environment (development/production)

### OpenSky Network
- Rate Limits (Anonymous): 10 requests / 10 seconds
- Rate Limits (Authenticated): 4000 credits / day
- API Documentation: https://openskynetwork.github.io/opensky-api/

### Distance Calculations
- Default radius: 50 nautical miles
- Maximum radius: 250 nautical miles
- Uses great circle distance (haversine formula)

## 🚨 Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include descriptive messages:

```json
{
  "error": "Invalid coordinates provided",
  "status": 400
}
```

## 📊 Data Quality Notes

- **Coverage**: ADS-B data quality depends on ground station coverage
- **Military Aircraft**: Most military flights won't appear in ADS-B data
- **Altitude**: Barometric altitude in meters above sea level
- **Velocity**: Ground speed in m/s
- **Updates**: Real-time data updated every few seconds

## 🔐 Security Recommendations

- Never commit `.env` file to version control
- Use environment variables for all sensitive credentials
- Enable authentication for production deployments
- Implement rate limiting for public APIs
- Use HTTPS in production environments

## 🚀 Deployment

### Local Development
```bash
python3 app.py
```

### Production (using Gunicorn)
```bash
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Cloud Deployment Options
- **Heroku**: Easy deployment with Procfile
- **Railway**: Simple git-based deployment
- **Render**: Free tier with automatic SSL
- **AWS EC2/ECS**: Full control and scalability
- **Google Cloud Run**: Serverless container deployment

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🔗 Resources

- [OpenSky Network API Documentation](https://openskynetwork.github.io/opensky-api/)
- [Mistral AI Documentation](https://docs.mistral.ai/)
- [ADS-B Technology Overview](https://en.wikipedia.org/wiki/Automatic_Dependent_Surveillance%E2%80%93Broadcast)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 👥 Author

Created by @rkijak

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Happy Aircraft Tracking!** ✈️
