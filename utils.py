import math
from datetime import datetime
from config import Config

def nautical_miles_to_degrees(nm):
    """Convert nautical miles to approximate degrees"""
    return nm * Config.NM_TO_DEGREES

def calculate_bounding_box(latitude, longitude, radius_nm):
    """
    Calculate bounding box from center point and radius
    
    Args:
        latitude (float): Center latitude
        longitude (float): Center longitude
        radius_nm (float): Radius in nautical miles
        
    Returns:
        tuple: (min_lat, max_lat, min_lon, max_lon)
    """
    radius_deg = nautical_miles_to_degrees(radius_nm)
    
    # Adjust longitude for latitude (longitude degrees get smaller near poles)
    lon_adjustment = radius_deg / math.cos(math.radians(latitude))
    
    return (
        latitude - radius_deg,   # min_latitude
        latitude + radius_deg,   # max_latitude
        longitude - lon_adjustment,  # min_longitude
        longitude + lon_adjustment   # max_longitude
    )

def haversine_distance(lat1, lon1, lat2, lon2, unit='nm'):
    """
    Calculate great circle distance between two points
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        unit: 'nm' (nautical miles), 'km' (kilometers), or 'mi' (statute miles)
        
    Returns:
        float: Distance in specified unit
    """
    R = 6371  # Earth radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    distance_km = R * c
    
    if unit == 'nm':
        return distance_km * 0.539957  # km to nautical miles
    elif unit == 'mi':
        return distance_km * 0.621371  # km to statute miles
    else:
        return distance_km

def format_aircraft_state(state):
    """Format OpenSky StateVector into readable dict"""
    if not state:
        return None
        
    return {
        'icao24': state.icao24,
        'callsign': state.callsign.strip() if state.callsign else None,
        'origin_country': state.origin_country,
        'time_position': state.time_position,
        'last_contact': state.last_contact,
        'longitude': state.longitude,
        'latitude': state.latitude,
        'baro_altitude': state.baro_altitude,  # meters
        'on_ground': state.on_ground,
        'velocity': state.velocity,  # m/s
        'true_track': state.true_track,  # degrees
        'vertical_rate': state.vertical_rate,  # m/s
        'squawk': state.squawk,
        'altitude_feet': round(state.baro_altitude / Config.FEET_TO_METERS) if state.baro_altitude else None,
        'velocity_knots': round(state.velocity / Config.KNOTS_TO_MS) if state.velocity else None
    }

def iso_to_unix(iso_string):
    """Convert ISO 8601 string to Unix timestamp"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return int(dt.timestamp())
    except:
        return None
