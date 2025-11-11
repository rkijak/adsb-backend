import requests
from config import Config
from utils import calculate_bounding_box, haversine_distance, iso_to_unix
import time

class OpenSkyService:
    def __init__(self):
        """Initialize OpenSky API client"""
        self.base_url = "https://opensky-network.org/api"
        self.auth = None
        if Config.OPENSKY_USERNAME and Config.OPENSKY_PASSWORD:
            self.auth = (Config.OPENSKY_USERNAME, Config.OPENSKY_PASSWORD)
    
    def _format_state_vector(self, state):
        """Format state vector from OpenSky API response"""
        if not state or len(state) < 17:
            return None
        
        return {
            'icao24': state[0],
            'callsign': state[1].strip() if state[1] else None,
            'origin_country': state[2],
            'time_position': state[3],
            'last_contact': state[4],
            'longitude': state[5],
            'latitude': state[6],
            'baro_altitude': state[7],  # meters
            'on_ground': state[8],
            'velocity': state[9],  # m/s
            'true_track': state[10],  # degrees
            'vertical_rate': state[11],  # m/s
            'sensors': state[12],
            'geo_altitude': state[13],
            'squawk': state[14],
            'spi': state[15],
            'position_source': state[16],
            'altitude_feet': round(state[7] / Config.FEET_TO_METERS) if state[7] else None,
            'velocity_knots': round(state[9] / Config.KNOTS_TO_MS) if state[9] else None
        }
    
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
            
            # Call OpenSky API
            params = {
                'lamin': bbox[0],
                'lamax': bbox[1],
                'lomin': bbox[2],
                'lomax': bbox[3]
            }
            
            response = requests.get(
                f"{self.base_url}/states/all",
                params=params,
                auth=self.auth,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            if not data or not data.get('states'):
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
            for state in data['states']:
                formatted = self._format_state_vector(state)
                if not formatted:
                    continue
                
                # Apply altitude filters
                if altitude_min and formatted['altitude_feet']:
                    if formatted['altitude_feet'] < altitude_min:
                        continue
                
                if altitude_max and formatted['altitude_feet']:
                    if formatted['altitude_feet'] > altitude_max:
                        continue
                
                # Apply aircraft type filter
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
                'timestamp': data.get('time', int(time.time())),
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
            
            params = {'icao24': icao24} if icao24 else {}
            
            response = requests.get(
                f"{self.base_url}/states/all",
                params=params,
                auth=self.auth,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            if not data or not data.get('states'):
                return {
                    'success': False,
                    'error': 'Aircraft not found or not currently transmitting',
                    'identifier': identifier
                }
            
            state = data['states'][0]
            formatted = self._format_state_vector(state)
            
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
            
            icao24 = flight_id.lower()
            
            response = requests.get(
                f"{self.base_url}/flights/aircraft",
                params={'icao24': icao24, 'begin': begin, 'end': end},
                auth=self.auth,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            flights = response.json()
            
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
                    'icao24': flight.get('icao24'),
                    'callsign': flight.get('callsign', '').strip() if flight.get('callsign') else None,
                    'departure_airport': flight.get('estDepartureAirport'),
                    'arrival_airport': flight.get('estArrivalAirport'),
                    'first_seen': flight.get('firstSeen'),
                    'last_seen': flight.get('lastSeen'),
                    'departure_time_utc': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(flight.get('firstSeen'))) if flight.get('firstSeen') else None,
                    'arrival_time_utc': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(flight.get('lastSeen'))) if flight.get('lastSeen') else None
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
            
            end_time = int(time.time())
            begin_time = end_time - (2 * 3600)
            
            if include_arrivals:
                try:
                    response = requests.get(
                        f"{self.base_url}/flights/arrival",
                        params={'airport': airport_code, 'begin': begin_time, 'end': end_time},
                        auth=self.auth,
                        timeout=Config.REQUEST_TIMEOUT
                    )
                    response.raise_for_status()
                    arrivals = response.json()
                    
                    result['arrivals'] = {
                        'count': len(arrivals) if arrivals else 0,
                        'flights': [
                            {
                                'icao24': f.get('icao24'),
                                'callsign': f.get('callsign', '').strip() if f.get('callsign') else None,
                                'departure_airport': f.get('estDepartureAirport'),
                                'arrival_time': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(f.get('lastSeen'))) if f.get('lastSeen') else None
                            }
                            for f in (arrivals[:10] if arrivals else [])
                        ]
                    }
                except:
                    result['arrivals'] = {'count': 0, 'error': 'Unable to fetch arrivals'}
            
            if include_departures:
                try:
                    response = requests.get(
                        f"{self.base_url}/flights/departure",
                        params={'airport': airport_code, 'begin': begin_time, 'end': end_time},
                        auth=self.auth,
                        timeout=Config.REQUEST_TIMEOUT
                    )
                    response.raise_for_status()
                    departures = response.json()
                    
                    result['departures'] = {
                        'count': len(departures) if departures else 0,
                        'flights': [
                            {
                                'icao24': f.get('icao24'),
                                'callsign': f.get('callsign', '').strip() if f.get('callsign') else None,
                                'arrival_airport': f.get('estArrivalAirport'),
                                'departure_time': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(f.get('firstSeen'))) if f.get('firstSeen') else None
                            }
                            for f in (departures[:10] if departures else [])
                        ]
                    }
                except:
                    result['departures'] = {'count': 0, 'error': 'Unable to fetch departures'}
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
