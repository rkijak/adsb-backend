from mistralai import Mistral
import requests
import json
import os

# Initialize Mistral client with your API key from environment variable
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is required. Please set it in your .env file.")

client = Mistral(api_key=MISTRAL_API_KEY)

# Your Flask backend URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5001')

# Function implementations that call your Flask backend
def collect_adsb_data(latitude, longitude, radius, altitude_min=None, altitude_max=None, aircraft_type=None):
    """Call Flask API to collect ADS-B data"""
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'radius': radius
    }
    if altitude_min:
        params['altitude_min'] = altitude_min
    if altitude_max:
        params['altitude_max'] = altitude_max
    if aircraft_type:
        params['aircraft_type'] = aircraft_type
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/collect_adsb_data", params=params, timeout=30)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_aircraft_info(identifier, identifier_type):
    """Call Flask API to get aircraft info"""
    params = {
        'identifier': identifier,
        'identifier_type': identifier_type
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/aircraft/{identifier}", params=params, timeout=30)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_flight_history(aircraft_id, begin_time, end_time):
    """Call Flask API to get flight history"""
    params = {
        'begin': begin_time,
        'end': end_time
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/flights/{aircraft_id}", params=params, timeout=30)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_airport_operations(airport_icao, begin_time, end_time, operation_type='both'):
    """Call Flask API to get airport arrivals/departures"""
    params = {
        'begin': begin_time,
        'end': end_time,
        'type': operation_type
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/airport/{airport_icao}", params=params, timeout=30)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def calculate_distance(lat1, lon1, lat2, lon2):
    """Call Flask API to calculate distance between two points"""
    params = {
        'lat1': lat1,
        'lon1': lon1,
        'lat2': lat2,
        'lon2': lon2
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/distance", params=params, timeout=30)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

# Tool definitions for Mistral AI
tools = [
    {
        "type": "function",
        "function": {
            "name": "collect_adsb_data",
            "description": "Collect ADS-B data for aircraft within a specified geographic area",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number", "description": "Latitude of search center"},
                    "longitude": {"type": "number", "description": "Longitude of search center"},
                    "radius": {"type": "number", "description": "Search radius in nautical miles"},
                    "altitude_min": {"type": "number", "description": "Minimum altitude filter (optional)"},
                    "altitude_max": {"type": "number", "description": "Maximum altitude filter (optional)"},
                    "aircraft_type": {"type": "string", "description": "Filter by aircraft type (optional)"}
                },
                "required": ["latitude", "longitude", "radius"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_aircraft_info",
            "description": "Get detailed information about a specific aircraft",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {"type": "string", "description": "Aircraft identifier (ICAO24 address or callsign)"},
                    "identifier_type": {"type": "string", "enum": ["icao24", "callsign"], "description": "Type of identifier"}
                },
                "required": ["identifier", "identifier_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_flight_history",
            "description": "Get flight history for a specific aircraft",
            "parameters": {
                "type": "object",
                "properties": {
                    "aircraft_id": {"type": "string", "description": "Aircraft ICAO24 address"},
                    "begin_time": {"type": "integer", "description": "Start time (Unix timestamp)"},
                    "end_time": {"type": "integer", "description": "End time (Unix timestamp)"}
                },
                "required": ["aircraft_id", "begin_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_airport_operations",
            "description": "Get arrivals and departures for a specific airport",
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_icao": {"type": "string", "description": "Airport ICAO code (e.g., KJFK)"},
                    "begin_time": {"type": "integer", "description": "Start time (Unix timestamp)"},
                    "end_time": {"type": "integer", "description": "End time (Unix timestamp)"},
                    "operation_type": {"type": "string", "enum": ["arrivals", "departures", "both"], "description": "Type of operations"}
                },
                "required": ["airport_icao", "begin_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_distance",
            "description": "Calculate distance between two geographic coordinates",
            "parameters": {
                "type": "object",
                "properties": {
                    "lat1": {"type": "number", "description": "First point latitude"},
                    "lon1": {"type": "number", "description": "First point longitude"},
                    "lat2": {"type": "number", "description": "Second point latitude"},
                    "lon2": {"type": "number", "description": "Second point longitude"}
                },
                "required": ["lat1", "lon1", "lat2", "lon2"]
            }
        }
    }
]

def run_agent(user_message):
    """Run the Mistral AI agent with function calling"""
    messages = [
        {"role": "user", "content": user_message}
    ]
    
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    # Process tool calls
    while response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"\nCalling function: {function_name}")
            print(f"Arguments: {function_args}")
            
            # Call the appropriate function
            if function_name == "collect_adsb_data":
                result = collect_adsb_data(**function_args)
            elif function_name == "get_aircraft_info":
                result = get_aircraft_info(**function_args)
            elif function_name == "get_flight_history":
                result = get_flight_history(**function_args)
            elif function_name == "get_airport_operations":
                result = get_airport_operations(**function_args)
            elif function_name == "calculate_distance":
                result = calculate_distance(**function_args)
            else:
                result = {"error": "Unknown function"}
            
            # Add function result to messages
            messages.append({
                "role": "tool",
                "name": function_name,
                "content": json.dumps(result)
            })
        
        # Get next response
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    print("ADS-B Aircraft Tracking Agent")
    print("==============================")
    print("Ask questions about aircraft, flights, and airports.")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        try:
            response = run_agent(user_input)
            print(f"\nAgent: {response}\n")
        except Exception as e:
            print(f"\nError: {e}\n")
