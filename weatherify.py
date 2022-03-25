import weather_access as wa
import spotify_access as sa

def main():
    city_name = "Longyearbyen"
    state = None
    country = ""
    api_key = "9aa9c73a693fdf0ac41fe665656c090c"
    lat, lon = wa.get_lat_lon_from_input(key=api_key, city=city_name, country=country)
    if lat != None:
        five_day_data_dict = wa.get_5_day_data(api_key, lat, lon)
        print(five_day_data_dict)
        print(lat, lon)

if __name__ == "__main__":
    main()