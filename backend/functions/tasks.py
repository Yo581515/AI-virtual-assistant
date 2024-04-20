from datetime import datetime, timezone, UTC
import dotenv
import pytz

dotenv.load_dotenv()
import os
from pyflightdata import FlightData
import requests
import json
import python_weather
import asyncio
from api_requests import local_time_and_air_temperature


def get_local_time():
    return datetime.now().strftime("day/month: %d/%m clock: %H:%M:%S")

def get_flight_info(origin, destination):
    f=FlightData()
    f.login(email=os.getenv("EMAIL"), password=os.getenv("PASSWORD"))
    
    flights = [{'departure_time': flight['time']['scheduled']['departure_time'] + " " + flight['time']['scheduled']['departure_date']} for flight in f.get_flights_from_to(origin=origin, destination=destination) if datetime.strptime(flight['time']['scheduled']['departure_date'] + ' ' + flight['time']['scheduled']['departure_time'], "%Y%m%d %H%M").replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)]

    for flight in flights:
        time = datetime.strptime(flight['departure_time'], "%H%M %Y%m%d")
        time = time.replace(tzinfo=timezone.utc).astimezone()
        flight['departure_time'] = time.strftime("%H:%M %d/%m/%y")
    
    return flights[0]["departure_time"] if flights else "No flights available"

def get_cheapest_flight(origin, destination):
    url = "https://skyscanner80.p.rapidapi.com/api/v1/flights/search-one-way"

    from_id = find_airport_id(origin)
    to_id = find_airport_id(destination)
    depart_date = datetime.now(UTC).strftime("%Y-%m-%d")

    querystring = {"fromId":from_id,"toId":to_id,"departDate":depart_date,"adults":"1","currency":"USD","market":"US","locale":"en-US"}

    headers = {
	    "X-RapidAPI-Key": "dcdc53af85msh365c2e7df63f3a1p1c1125jsn09a2b383ea11",
	    "X-RapidAPI-Host": "skyscanner80.p.rapidapi.com"
    }

    response =  requests.get(url, headers=headers, params=querystring).json()
    flights = response["data"]["itineraries"]
    lowest_price_flight = [flight for flight in flights if flight["price"]["raw"] == min([flight["price"]["raw"] for flight in flights])][0]

    marketing_carrier_name = lowest_price_flight['legs'][0]['carriers']['marketing'][0]['name']
    formatted_price = lowest_price_flight['price']['formatted']
    departure_time = lowest_price_flight['legs'][0]['departure']

    return marketing_carrier_name, formatted_price, departure_time

def find_airport_id(city):
    url = "https://skyscanner80.p.rapidapi.com/api/v1/flights/auto-complete"

    querystring = {"query":city,"market":"US","locale":"en-US"}

    headers = {
	    "X-RapidAPI-Key": "dcdc53af85msh365c2e7df63f3a1p1c1125jsn09a2b383ea11",
	    "X-RapidAPI-Host": "skyscanner80.p.rapidapi.com"
    }

    return requests.get(url, headers=headers, params=querystring).json()["data"][0]["id"]
    
async def get_weather(city):
    async with python_weather.Client() as client:
        
        weather = await client.get(city)
        
        return "Precipitation: " + str(weather.precipitation) + "mm, temperature: " + str(weather.temperature) + "C, humidity: " + str(weather.humidity) + "%, wind speed: " + str(weather.wind_speed) + "kph, description: " + weather.description



def date_time_now():
    # Define Norway's timezone
    norway_timezone = pytz.timezone('Europe/Oslo')

    # Get the current date and time
    now = datetime.datetime.now(norway_timezone)

    # Prepare date and time information
    date_info = {
        "Current Date and Time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "Year": now.year,
        "Month": now.month,
        "Day of the Month": now.day,
        "Hour": now.hour,
        "Minute": now.minute,
        "Second": now.second,
        "Microsecond": now.microsecond,
        "Day of the Week (index)": now.weekday(),  # Monday is 0, Sunday is 6
        "Day of the Week (name)": now.strftime("%A"),  # Full weekday name
        "ISO Day of the Week": now.isoweekday(),  # Monday is 1, Sunday is 7
        "Week Number of the Year (ISO)": now.isocalendar()[1],  # ISO week number
        "ISO Year": now.isocalendar()[0],
        "ISO Weekday": now.isocalendar()[2]  # ISO weekday
    }

    # Convert to JSON string
    json_string = json.dumps(date_info, indent=4)

    # print(json_string)

    return json_string


def local_temperature_info():
    current_time_info = date_time_now()
    forcast_data = local_time_and_air_temperature()

    my_location_weather_wather_info = {
        "current_time_info": current_time_info,
        "forcast_data": forcast_data
    }

    # print(my_location_weather_wather_info)

    return my_location_weather_wather_info
