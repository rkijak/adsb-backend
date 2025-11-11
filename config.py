import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenSky Network credentials (optional - improves rate limits)
    OPENSKY_USERNAME = os.getenv('OPENSKY_USERNAME', None)
    OPENSKY_PASSWORD = os.getenv('OPENSKY_PASSWORD', None)
    
    # Flask settings
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # API settings
    REQUEST_TIMEOUT = 30  # seconds
    
    # Constants
    NM_TO_DEGREES = 0.0167  # 1 nautical mile ≈ 0.0167 degrees
    KNOTS_TO_MS = 0.514444  # 1 knot = 0.514444 m/s
    FEET_TO_METERS = 0.3048  # 1 foot = 0.3048 meters
