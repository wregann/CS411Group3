import api.weather_access as wa
import api.spotify_access as sa
import creds
from flask import Flask, send_from_directory, render_template
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS #comment this on deployment
from api.weatherify_api_handler import WeatherifyApiHandler

def elloMate():
    # city_name = "Longyearbyen"
    # state = None
    # country = ""
    # api_key = "9aa9c73a693fdf0ac41fe665656c090c"
    # lat, lon = wa.get_lat_lon_from_input(key=api_key, city=city_name, country=country)
    # if lat != None:
    #     five_day_data_dict = wa.get_5_day_data(api_key, lat, lon)
    #     print(five_day_data_dict)
    #     print(lat, lon)
    pass

app = Flask(__name__)
#CORS(app) #comment this on deployment
#api = Api(app)

@app.route("/")
def serve(path):
    return render_template('example.html', value=wa.get_5_days())

@app.route("/events/weather_data/<city_string>", methods = ['GET'])
def get_weather_data(city_string):
    wa.get_lat_lon_from_input()

#api.add_resource(WeatherifyApiHandler, '/flask/hello')

if __name__ == "__main__":
    app.run(port=1000, debug=True)