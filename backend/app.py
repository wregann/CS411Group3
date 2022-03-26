from multiprocessing.sharedctypes import Value
import weather_access as wa
import spotify_access as sa
import backend.creds as creds
from flask import Flask, send_from_directory, render_template
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS #comment this on deployment


app = Flask(__name__)
#CORS(app) #comment this on deployment
#api = Api(app)

@app.route("/")
def serve(path):
    return render_template('example.html', value=wa.get_5_days())

@app.route("/events/weather_data/<city_string>", methods = ['GET'])
def get_weather_data(city_string):
    try:
        lat, lon = wa.get_lat_lon_from_input(key=creds.openweather_key, city=city_string)
    except ValueError as e:
        print(e)
        return 'Error: Could not get city longitude and latitude, please try agian'
    
    try:
        five_day_data_dict = wa.get_5_day_data(key=creds.openweather_key, lat=lat, lon=lon)
    except ValueError as e:
        print(e)
        return 'Error: could not get weather data from latitude and lognitude'
    
    return five_day_data_dict

if __name__ == "__main__":
    app.run(port=1000, debug=True)