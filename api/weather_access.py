import json, requests
from typing import Tuple

def get_lat_lon_from_input(key: str, city: str, state: str = "", country: str = "") -> Tuple[float, float]:
    """
    Given a valid open weather api key, city name, state (not needed), and country (not needed)
    returns the latitude and longitude of the names place.
    
    Parameters:
    key - the api key to openweather
    city - string of city name
    state - state code, only if place is in US (ex. MA)
    country - country code (ex. US, CA, GB)
    
    Returns:
    Tuple(Latitude, Longitude)
    """
    if all(x.isalpha() or x.isspace() for x in city + state + country):
        base_url = "http://api.openweathermap.org/geo/1.0/direct?q="
        limit = 1
        loc = city.lower()
        if state != "":
            loc = loc + ", " + state
        if country != "":
            loc = loc + ", " + country
        complete_url = base_url + loc + "&limit=" + str(limit) + "&appid=" + key
        response = requests.get(complete_url)
        city_data_list = response.json()
        # Check if valid, return values
        if len(city_data_list) != 0:
            city_data_dict = city_data_list[0]
            return city_data_dict["lat"], city_data_dict["lon"]
        else:
            print("Error in Getting City From Input. Try fixing spelling or spacing!")
            return None, None
    else:
        raise ValueError("Your inputs contain non-alphabetic or space characters")

def get_5_day_data(key: str, lat: float, lon: float) -> dict:
    """"
    Given an api key, latitude, and longitude, this will return the weather data for the next five days
    
    Parameters:
    key - openweather api key string
    lat - latitude number
    lon - longitude number
    
    Returns:
    5 day weather dictionary
    """
    base_url = "https://api.openweathermap.org/data/2.5/onecall?lat="
    complete_url = base_url + str(lat) + "&lon=" + str(lon) + "&exclude=current,minutely,hourly,alerts&appid=" + key
    response = requests.get(complete_url)
    five_day_data = response.json()
    return five_day_data





