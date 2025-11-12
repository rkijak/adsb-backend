from mistralai import Mistral
import requests
import json
import os

# Initialize Mistral client with your API key
MISTRAL_API_KEY = "y9xgcbtfmf8VFXq7ydHgEVlf15Z1C1X0"
client = Mistral(api_key=MISTRAL_API_KEY)

# Your Flask backend URL
BACKEND_URL = "http://localhost:5001"

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
        response = requests.get(f"{BACKEND_URL}/api/get_aircraft_info", params=params, timeout=30)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_flight_history(flight_id, start_time, end_time):
    """Call Flask API to get flight history"""
    params = {
        'flight_id': flight_id,
        'start_time': start_time,
        'end_time': end_time
    }
    try:
        response = requests.get(f"{BACKEND_URL}/api/get_flight_history", params=params, timeout=30)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_airport_info(airport_code, include_weather=True, include_departures=False, include_arrivals=False):
    """Call Flask API to get airport info"""
    params = {
        'airport_code': airport_code,
        'include_weather': str(include_weather).lower(),
        'include_departures': str(include_departures).lower(),
        'include_arrivals': str(include_arrivals).lower()
    }
    try:
        response = requests.get(f"{BACKEND_URL}/api/get_airport_info", params=params, timeout=30)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def calculate_route_distance(origin, destination, unit='nautical_miles', average_speed_knots=450):
    """Call Flask API to calculate route distance"""
    params = {
        'origin': origin,
        'destination': destination,
        'unit': unit,
        'average_speed_knots': average_speed_knots
    }
    try:
        response = requests.get(f"{BACKEND_URL}/api/calculate_route_distance", params=params, timeout=30)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

# Function definitions for Mistral AI
tools = [
    {
        "type": "function",
        "function": {
            "name": "collect_adsb_data",
            "description": "Collects ADS-B (Automatic Dependent Surveillance-Broadcast) data for aircraft tracking, including position, altitude, speed, and identification information",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number", "description": "Latitude coordinate for the center of the search area in decimal degrees"},
                    "longitude": {"type": "number", "description": "Longitude coordinate for the center of the search area in decimal degrees"},
                    "radius": {"type": "number", "description": "Search radius in nautical miles from the center point"},
                    "altitude_min": {"type": "number", "description": "Minimum altitude filter in feet (optional)"},
                    "altitude_max": {"type": "number", "description": "Maximum altitude filter in feet (optional)"},
                    "aircraft_type": {"type": "string", "description": "Filter by aircraft type or ICAO code (optional)"}
                },
                "required": ["latitude", "longitude", "radius"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_aircraft_info",
            "description": "Retrieves detailed information about a specific aircraft including registration, model, operator, and technical specifications",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {"type": "string", "description": "Aircraft identifier - can be flight number (e.g., 'AA123'), ICAO24 hex code, or registration (e.g., 'N12345')"},
                    "identifier_type": {"type": "string", "enum": ["flight_number", "icao24", "registration"], "description": "Type of identifier being provided"}
                },
                "required": ["identifier", "identifier_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_flight_history",
            "description": "Retrieves historical flight path and trajectory data for a specific flight, including waypoints, timestamps, and altitude changes",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_id": {"type": "string", "description": "Flight number or ICAO24 hex code"},
                    "start_time": {"type": "string", "description": "Start time for history query in ISO 8601 format (e.g., '2025-11-10T12:00:00Z')"},
                    "end_time": {"type": "string", "description": "End time for history query in ISO 8601 format (e.g., '2025-11-11T12:00:00Z')"}
                },
                "required": ["flight_id", "start_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_airport_info",
            "description": "Retrieves information about airports including location, runways, weather conditions, and current flight operations",
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_code": {"type": "string", "description": "Airport ICAO or IATA code (e.g., 'KJFK', 'JFK', 'KSFO')"},
                    "include_weather": {"type": "boolean", "description": "Include current weather conditions (default: true)"},
                    "include_departures": {"type": "boolean", "description": "Include departure information (default: false)"},
                    "include_arrivals": {"type": "boolean", "description": "Include arrival information (default: false)"}
                },
                "required": ["airport_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_route_distance",
            "description": "Calculates the great circle distance and estimated flight time between two points or airports",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin point - can be airport code (e.g., 'JFK') or coordinates as 'lat,lon'"},
                    "destination": {"type": "string", "description": "Destination point - can be airport code (e.g., 'LAX') or coordinates as 'lat,lon'"},
                    "unit": {"type": "string", "enum": ["nautical_miles", "kilometers", "statute_miles"], "description": "Distance unit (default: nautical_miles)"},
                    "average_speed_knots": {"type": "number", "description": "Average cruising speed in knots for time estimation (default: 450)"}
                },
                "required": ["origin", "destination"]
            }
        }
    }
]

# Map function names to actual implementations
function_map = {
    "collect_adsb_data": collect_adsb_data,
    "get_aircraft_info": get_aircraft_info,
    "get_flight_history": get_flight_history,
    "get_airport_info": get_airport_info,
    "calculate_route_distance": calculate_route_distance
}

def chat_with_agent(user_message):
    """Chat with the ADS-B agent"""
    system_prompt = """You are an expert ADS-B Aircraft Tracking Assistant specialized in monitoring and analyzing aircraft movements worldwide using real-time ADS-B (Automatic Dependent Surveillance-Broadcast) data.

YOUR ROLE:
Provide accurate, timely information about aircraft positions, flight paths, airport operations, and aviation data. Help users track specific flights, monitor airspace activity, analyze flight history, and answer questions about aircraft and airports.

BEST PRACTICES:
- Always confirm location details (use coordinates when possible)
- Specify appropriate search radius based on the context (e.g., 50nm for local area, 200nm for regional)
- Use current timestamp (November 11, 2025, 8 PM CST) for time-sensitive queries
- Provide altitude in feet, distance in nautical miles (unless user specifies otherwise)
- Include relevant context like aircraft type, airline, departure/destination when available
- For time ranges, use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)

COMMUNICATION STYLE:
- Be precise and technical when appropriate
- Explain aviation terminology if the user seems unfamiliar
- Present data in clear, organized formats
- Proactively suggest related information that might be useful
- Always indicate data sources and timestamps"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    print(f"\n🤖 Processing: {user_message}\n")
    
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    # Handle function calls
    if response.choices[0].message.tool_calls:
        print(f"🔧 Function calls detected: {len(response.choices[0].message.tool_calls)}\n")
        
        for tool_call in response.choices[0].message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"📞 Calling: {function_name}")
            print(f"📋 Arguments: {json.dumps(function_args, indent=2)}")
            
            # Call the actual function
            function_result = function_map[function_name](**function_args)
            
            result_preview = json.dumps(function_result, indent=2)[:300]
            print(f"✅ Result preview: {result_preview}...\n")
            
            # Add function result to messages
            messages.append(response.choices[0].message.model_dump())
            messages.append({
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_result),
                "tool_call_id": tool_call.id
            })
        
        # Get final response
        print("🤔 Generating final response...\n")
        final_response = client.chat.complete(
            model="mistral-large-latest",
            messages=messages
        )
        return final_response.choices[0].message.content
    
    return response.choices[0].message.content

# Interactive chat mode
def interactive_mode():
    """Run interactive chat with the agent"""
    print("=" * 80)
    print("🛩️  ADS-B Aircraft Tracking Agent - Interactive Mode")
    print("=" * 80)
    print("\nExamples:")
    print("  - Show me aircraft near San Francisco within 50 nautical miles")
    print("  - What's the current status at JFK airport?")
    print("  - Calculate distance from San Francisco to New York")
    print("\nType 'exit' or 'quit' to end the session.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            response = chat_with_agent(user_input)
            print(f"\nAgent: {response}\n")
            print("-" * 80 + "\n")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command line mode
        query = " ".join(sys.argv[1:])
        result = chat_with_agent(query)
        print(f"\nAgent: {result}\n")
    else:
        # Interactive mode
        interactive_mode()
