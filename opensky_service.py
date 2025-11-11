from opensky_api import OpenSkyApi
from config import Config
from utils import calculate_bounding_box, format_aircraft_state, haversine_distance, iso_to_unix
import time

class OpenSkyService:
    def __init__(self):
        """Initialize OpenSky API client"""
        if Config.OPENSKY_USERNAME and Config.OPENSKY_PASSWORD:
            self.api = OpenSkyApi(
                username=Config.OPENSKY_USERNAME,
                password=Config.OPENSKY_PASSWORD
            )
        else:
            self.api = OpenSkyApi()  # Anonymous access
    
    def collect_adsb_data(self, latitude, longitude, radius, altitude_min=None, 
                         altitude_max=None, aircraft_type=None):
        """
        Collect ADS-B data in a geographic area
        
        Args:
            latitude (float): Center latitude
            longitude (float): Center longitude
            radius (float): Search radius in nautical miles
            altitude_min (float, optional): Minimum altitude in feet
            altitude_max (float, optional): Maximum altitude in feet
            aircraft_type (str, optional): Filter by aircraft type/ICAO code
            
        Returns:
            dict: Aircraft data and metadata
        """
        try:
            # Calculate bounding box
            bbox = calculate_bounding_box(latitude, longitude, radius)
            
            # Get states from OpenSky
            states = self.api.get_states(bbox=bbox)
            
            if not states:
                return {
                    'success': True,
                    'aircraft_count': 0,
                    'aircraft': [],
                    'search_area': {
                        'center': {'latitude': latitude, 'longitude': longitude},
                        'radius_nm': radius
                    }
                }
            
            # Format and filter aircraft
            aircraft = []
            for state in states.states:
                formatted = format_aircraft_state(state)
                
                # Apply altitude filters
                if altitude_min and formatted['altitude_feet']:
                    if formatted['altitude_feet'] < altitude_min:
                        continue
                
                if altitude_max and formatted['altitude_feet']:
                    if formatted['altitude_feet'] > altitude_max:
                        continue
                
                # Apply aircraft type filter (matches against ICAO24 or callsign)
                if aircraft_type:
                    if aircraft_type.lower() not in (formatted['icao24'].lower() if formatted['icao24'] else ''):
                        if aircraft_type.upper() not in (formatted['callsign'] or ''):
                            continue
                
                # Calculate distance from center
                if formatted['latitude'] and formatted['longitude']:
                    formatted['distance_from_center_nm'] = round(
                        haversine_distance(latitude, longitude, 
                                         formatted['latitude'], formatted['longitude']),
                        2
                    )
                
                aircraft.append(formatted)
            
            return {
                'success': True,
                'timestamp': int(time.time()),
                'aircraft_count': len(aircraft),
                'aircraft': aircraft,
                'search_area': {
                    'center': {'latitude': latitude, 'longitude': longitude},
                    'radius_nm': radius,
                    'bounding_box': {
                        'min_lat': bbox[0],
                        'max_lat': bbox[1],
                        'min_lon': bbox[2],
                        'max_lon': bbox[3]
                    }
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'aircraft_count': 0,
                'aircraft': []
            }
    
    def get_aircraft_info(self, identifier, identifier_type):
        """
        Get detailed aircraft information
        
        Args:
            identifier (str): Aircraft identifier
            identifier_type (str): 'flight_number', 'icao24', or 'registration'
            
        Returns:
            dict: Aircraft information
        """
        try:
            icao24 = identifier.lower() if identifier_type == 'icao24' else None
            
            # Get current state for this aircraft
            states = self.api.get_states(icao24=icao24)
            
            if not states or not states.states:
                return {
                    'success': False,
                    'error': 'Aircraft not found or not currently transmitting',
                    'identifier': identifier
                }
            
            # Get the first matching state
            state = states.states[0]
            formatted = format_aircraft_state(state)
            
            # Try to get recent flight history
            end_time = int(time.time())
            begin_time = end_time - (24 * 3600)  # Last 24 hours
            
            try:
                flights = self.api.get_flights_by_aircraft(icao24, begin_time, end_time)
                formatted['recent_flights'] = len(flights) if flights else 0
            except:
                formatted['recent_flights'] = None
            
            return {
                'success': True,
                'aircraft': formatted,
                'identifier_type': identifier_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'identifier': identifier
            }
    
    def get_flight_history(self, flight_id, start_time, end_time):
        """
        Get historical flight path data
        
        Args:
            flight_id (str): Flight number or ICAO24
            start_time (str): Start time in ISO 8601 format
            end_time (str): End time in ISO 8601 format
            
        Returns:
            dict: Flight history data
        """
        try:
            begin = iso_to_unix(start_time)
            end = iso_to_unix(end_time)
            
            if not begin or not end:
                return {
                    'success': False,
                    'error': 'Invalid time format. Use ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)'
                }
            
            # Try to get flights
            icao24 = flight_id.lower()
            flights = self.api.get_flights_by_aircraft(icao24, begin, end)
            
            if not flights:
                return {
                    'success': True,
                    'flight_count': 0,
                    'flights': [],
                    'message': 'No flights found in specified time range'
                }
            
            formatted_flights = []
            for flight in flights:
                formatted_flights.append({
                    'icao24': flight.icao24,
                    'callsign': flight.callsign.strip() if flight.callsign else None,
                    'departure_airport': flight.estDepartureAirport,
                    'arrival_airport': flight.estArrivalAirport,
                    'first_seen': flight.firstSeen,
                    'last_seen': flight.lastSeen,
                    'departure_time_utc': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(flight.firstSeen)) if flight.firstSeen else None,
                    'arrival_time_utc': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(flight.lastSeen)) if flight.lastSeen else None
                })
            
            return {
                'success': True,
                'flight_count': len(formatted_flights),
                'flights': formatted_flights,
                'query': {
                    'flight_id': flight_id,
                    'start_time': start_time,
                    'end_time': end_time
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_airport_info(self, airport_code, include_weather=True, 
                        include_departures=False, include_arrivals=False):
        """
        Get airport information
        
        Args:
            airport_code (str): ICAO or IATA airport code
            include_weather (bool): Include weather data
            include_departures (bool): Include departure info
            include_arrivals (bool): Include arrival info
            
        Returns:
            dict: Airport information
        """
        try:
            airport_code = airport_code.upper()
            
            result = {
                'success': True,
                'airport_code': airport_code,
                'timestamp': int(time.time())
            }
            
            # Get current time and 2-hour window
            end_time = int(time.time())
            begin_time = end_time - (2 * 3600)  # Last 2 hours
            
            if include_arrivals:
                try:
                    arrivals = self.api.get_arrivals_by_airport(airport_code, begin_time, end_time)
                    result['arrivals'] = {
                        'count': len(arrivals) if arrivals else 0,
                        'flights': [
                            {
                                'icao24': f.icao24,
                                'callsign': f.callsign.strip() if f.callsign else None,
                                'departure_airport': f.estDepartureAirport,
                                'arrival_time': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(f.lastSeen)) if f.lastSeen else None
                            }
                            for f in (arrivals[:10] if arrivals else [])  # Limit to 10
                        ]
                    }
                except:
                    result['arrivals'] = {'count': 0, 'error': 'Unable to fetch arrivals'}
            
            if include_departures:
                try:
                    departures = self.api.get_departures_by_airport(airport_code, begin_time, end_time)
                    result['departures'] = {
                        'count': len(departures) if departures else 0,
                        'flights': [
                            {
                                'icao24': f.icao24,
                                'callsign': f.callsign.strip() if f.callsign else None,
                                'arrival_airport': f.estArrivalAirport,
                                'departure_time': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(f


