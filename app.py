from flask import Flask, request, jsonify
from flask_cors import CORS
from opensky_service import OpenSkyService
from config import Config
import math

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize OpenSky service
opensky_service = OpenSkyService()

@app.route('/')
def index():
    """API documentation endpoint"""
    return jsonify({
        'name': 'ADS-B Aircraft Tracking API',
        'version': '1.0.0',
        'description': 'Flask backend for ADS-B aircraft tracking with OpenSky Network API integration',
        'endpoints': {
            'collect_adsb_data': {
                'method': 'GET',
                'path': '/api/collect_adsb_data',
                'parameters': {
                    'latitude': 'float (required) - Center latitude',
                    'longitude': 'float (required) - Center longitude',
                    'radius': 'float (required) - Search radius in nautical miles',
                    'altitude_min': 'float (optional) - Minimum altitude in feet',
                    'altitude_max': 'float (optional) - Maximum altitude in feet',
                    'aircraft_type': 'string (optional) - Filter by aircraft type or ICAO code'
                },
                'example': '/api/collect_adsb_data?latitude=37.7749&longitude=-122.4194&radius=50'
            },
            'get_aircraft_info': {
                'method': 'GET',
                'path': '/api/get_aircraft_info',
                'parameters': {
                    'identifier': 'string (required) - Aircraft identifier',
                    'identifier_type': 'string (required) - Type: flight_number, icao24, or registration'
                },
                'example': '/api/get_aircraft_info?identifier=a1b2c3&identifier_type=icao24'
            },
            'get_flight_history': {
                'method': 'GET',
                'path': '/api/get_flight_history',
                'parameters': {
                    'flight_id': 'string (required) - Flight number or ICAO24',
                    'start_time': 'string (required) - ISO 8601 format',
                    'end_time': 'string (required) - ISO 8601 format'
                },
                'example': '/api/get_flight_history?flight_id=a1b2c3&start_time=2025-11-10T00:00:00Z&end_time=2025-11-11T00:00:00Z'
            },
            'get_airport_info': {
                'method': 'GET',
                'path': '/api/get_airport_info',
                'parameters': {
                    'airport_code': 'string (required) - ICAO or IATA code',
                    'include_weather': 'boolean (optional, default: true)',
                    'include_departures': 'boolean (optional, default: false)',
                    'include_arrivals': 'boolean (optional, default: false)'
                },
                'example': '/api/get_airport_info?airport_code=KSFO&include_arrivals=true'
            },
            'calculate_route_distance': {
                'method': 'GET',
                'path': '/api/calculate_route_distance',
                'parameters': {
                    'origin': 'string (required) - Airport code or lat,lon',
                    'destination': 'string (required) - Airport code or lat,lon',
                    'unit': 'string (optional) - nautical_miles, kilometers, or statute_miles',
                    'average_speed_knots': 'float (optional, default: 450)'
                },
                'example': '/api/calculate_route_distance?origin=KSFO&destination=KJFK'
            }
        }
    })

@app.route('/api/collect_adsb_data', methods=['GET'])
def collect_adsb_data():
    """Collect ADS-B data in a geographic area"""
    try:
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        radius = float(request.args.get('radius'))
        altitude_min = float(request.args.get('altitude_min')) if request.args.get('altitude_min') else None
        altitude_max = float(request.args.get('altitude_max')) if request.args.get('altitude_max') else None
        aircraft_type = request.args.get('aircraft_type')
        
        result = opensky_service.collect_adsb_data(
            latitude, longitude, radius, 
            altitude_min, altitude_max, aircraft_type
        )
        
        return jsonify(result)
        
    except TypeError as e:
        return jsonify({
            'success': False,
            'error': 'Missing or invalid required parameters. Required: latitude, longitude, radius',
            'details': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_aircraft_info', methods=['GET'])
def get_aircraft_info():
    """Get detailed aircraft information"""
    try:
        identifier = request.args.get('identifier')
        identifier_type = request.args.get('identifier_type')
        
        if not identifier or not identifier_type:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters: identifier and identifier_type'
            }), 400
        
        if identifier_type not in ['flight_number', 'icao24', 'registration']:
            return jsonify({
                'success': False,
                'error': 'Invalid identifier_type. Must be: flight_number, icao24, or registration'
            }), 400
        
        result = opensky_service.get_aircraft_info(identifier, identifier_type)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_flight_history', methods=['GET'])
def get_flight_history():
    """Get historical flight path data"""
    try:
        flight_id = request.args.get('flight_id')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        if not all([flight_id, start_time, end_time]):
            return jsonify({
                'success': False,
                'error': 'Missing required parameters: flight_id, start_time, end_time'
            }), 400
        
        result = opensky_service.get_flight_history(flight_id, start_time, end_time)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_airport_info', methods=['GET'])
def get_airport_info():
    """Get airport information"""
    try:
        airport_code = request.args.get('airport_code')
        
        if not airport_code:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: airport_code'
            }), 400
        
        include_weather = request.args.get('include_weather', 'true').lower() == 'true'
        include_departures = request.args.get('include_departures', 'false').lower() == 'true'
        include_arrivals = request.args.get('include_arrivals', 'false').lower() == 'true'
        
        result = opensky_service.get_airport_info(
            airport_code, 
            include_weather, 
            include_departures, 
            include_arrivals
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calculate_route_distance', methods=['GET'])
def calculate_route_distance():
    """Calculate distance and flight time between two points"""
    try:
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        
        if not all([origin, destination]):
            return jsonify({
                'success': False,
                'error': 'Missing required parameters: origin, destination'
            }), 400
        
        unit = request.args.get('unit', 'nautical_miles')
        average_speed_knots = float(request.args.get('average_speed_knots', 450))
        
        # Parse coordinates if provided as lat,lon
        def parse_location(loc):
            if ',' in loc:
                lat, lon = loc.split(',')
                return float(lat), float(lon)
            return None  # Airport code - would need airport database
        
        origin_coords = parse_location(origin)
        dest_coords = parse_location(destination)
        
        if not origin_coords or not dest_coords:
            return jsonify({
                'success': False,
                'error': 'Currently only supports lat,lon coordinates (e.g., "37.7749,-122.4194"). Airport code lookup coming soon.'
            }), 400
        
        # Calculate distance using haversine
        from utils import haversine_distance
        
        distance_nm = haversine_distance(
            origin_coords[0], origin_coords[1],
            dest_coords[0], dest_coords[1],
            unit='nm'
        )
        
        # Convert to requested unit
        if unit == 'kilometers':
            distance = distance_nm * 1.852
        elif unit == 'statute_miles':
            distance = distance_nm * 1.15078
        else:
            distance = distance_nm
        
        # Calculate flight time
        flight_time_hours = distance_nm / average_speed_knots
        
        result = {
            'success': True,
            'origin': {
                'input': origin,
                'coordinates': {'latitude': origin_coords[0], 'longitude': origin_coords[1]}
            },
            'destination': {
                'input': destination,
                'coordinates': {'latitude': dest_coords[0], 'longitude': dest_coords[1]}
            },
            'distance': round(distance, 2),
            'unit': unit,
            'flight_time': {
                'hours': round(flight_time_hours, 2),
                'minutes': round(flight_time_hours * 60, 0)
            },
            'calculation_parameters': {
                'average_speed_knots': average_speed_knots
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ADS-B Backend API',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print(f"Starting ADS-B Backend API on {Config.HOST}:{Config.PORT}")
    print(f"Debug mode: {Config.DEBUG}")
    print(f"API Documentation: http://{Config.HOST}:{Config.PORT}/")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
