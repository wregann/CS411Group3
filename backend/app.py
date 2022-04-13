from multiprocessing import AuthenticationError
from multiprocessing.sharedctypes import Value
import weather_access as wa
import creds
from flask import Flask, render_template, redirect, request, session, make_response,session,redirect
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS, cross_origin
from flask_session import Session
import spotipy
import arrow
import os
from flask_mysqldb import MySQL
import uuid
from marshmallow import Schema, fields, ValidationError
from urllib.parse import urlencode

class GoSchema(Schema):
    main = fields.String(required=True)
    description = fields.String(required=True)
    temperature = fields.Integer(required=True)
    
app = Flask(__name__, template_folder="../templates")

app.config['MYSQL_HOST'] = creds.DB_HOSTNAME
app.config['MYSQL_USER'] = creds.DB_USERNAME
app.config['MYSQL_PASSWORD'] = creds.DB_PASSWORD
app.config['MYSQL_DB'] = "WeatherifyDB"
app.config['SECRET_KEY'] = creds.APP_SECRET
app.config['SESSION_TYPE'] = 'filesystem'
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
# Set flask session cache directory, make it if it isnt there
if not os.path.exists('./.flask_session/'):
    os.makedirs('./.flask_session/')
app.config['SESSION_FILE_DIR'] = './.flask_session/'

mysql = MySQL(app)
app.secret_key = creds.APP_SECRET
API_BASE = 'https://accounts.spotify.com'
REDIRECT_URI = "http://127.0.0.1:1000/api/"
SCOPE = 'playlist-modify-private,playlist-modify-public,ugc-image-upload,user-library-read'

Session(app)


CORS(app, supports_credentials=True)
app.config['CORS_HEADERS'] = ['Content-Type', 'Authorization']

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    session_cache_path_string = caches_folder + session.get("uuid")
    if "not set" in session_cache_path_string:
        raise ValueError("not set in cache string")
    print("Session Cache Path: ", session_cache_path_string)
    return session_cache_path_string

@app.route("/api/", methods=['GET', 'POST'])
@cross_origin(methods=['GET', 'POST'], supports_credentials=True, headers=['Content-Type', 'Authorization'], origin='http://127.0.0.1:3000')
def index():
    print("----------------------------INDEX---------------------------------------------------")
    response = {"logged": False, "user_id": None, "auth_url": None}
            
    if session.get('uuid', None) == None:
        # Step 1. Visitor is unknown, give random ID
        print("Making User uuid")
        session['uuid'] = str(uuid.uuid4())
        session.modified = True
    else:
        print("User uuid still in session")
    print("Current uuid: ", session.get("uuid"))

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = creds.SPOTIFY_ID, client_secret = creds.SPOTIFY_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE, cache_handler=cache_handler, show_dialog=True)
    
    if request.args.get("code"):
        print("Code Received")
        # Step 3. Being redirected from Spotify auth page
        sp_oauth.get_access_token(request.args.get("code"))
        # Step 4. Signed in, display data
        response['logged'] = True
        sp = spotipy.Spotify(auth_manager=sp_oauth)
        print("Signed in with id: ", sp.me()['id'])
        response['user_id'] = sp.me()['id']
        #return response 
        return redirect("http://127.0.0.1:3000/", code=302)

    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = sp_oauth.get_authorize_url()
        print("sign in at : ", auth_url)
        response['logged'] = False
        response['auth_url'] = auth_url
    else:
        sp = spotipy.Spotify(auth_manager=sp_oauth)
        print("Signed in with id: ", sp.me()['id'])
        response['logged'] = True
        response['user_id'] = sp.me()['id']
    print("----------------------------END OF INDEX---------------------------------------------")
    return response


@app.route("/api/get_weather_data/<city_string>", methods = ['GET'])
def get_weather_data(city_string):
    response = {"lat": None, "lon": None}
    print("----------------------------GET WEATHER DATA--------------------------------")
    try:
        lat, lon = wa.get_lat_lon_from_input(key=creds.OPENWEATHER_KEY, city=city_string)
    except ValueError as e:
        print(e)
        print('Error: Could not get city longitude and latitude, please try again')
        return response
    
    try:
        five_day_data_dict = wa.get_5_day_data(key=creds.OPENWEATHER_KEY, lat=lat, lon=lon)
    except ValueError as e:
        print(e)
        print('Error: could not get weather data from latitude and lognitude')
        return response
    print("----------------------------END OF GET WEATHER DATA--------------------------------")
    return five_day_data_dict

# authorization-code-flow Step 1. Have your application request authorization; 
# the user logs in and authorizes access
@app.route("/api/spotify_login")
def verify():
    print("----------------------------SPOTIFY LOGIN VERIFY--------------------------------")
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    print("UUID HERE: ", session.get("uuid"))
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = creds.SPOTIFY_ID, client_secret = creds.SPOTIFY_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE, cache_handler=cache_handler)
    
    auth_url = sp_oauth.get_authorize_url()
    print("Going to auth_url")
    print(session['uuid'])
    print("----------------------------END OF SPOTIFY LOGIN VERIFY--------------------------------")
    return redirect(auth_url)

# authorization-code-flow Step 3.
# Use the access token to access the Spotify Web API;
# Spotify returns requested data
@app.route("/api/go", methods=['POST'])
@cross_origin(methods=['POST'], supports_credentials=True, headers=['Content-Type', 'Authorization'], origin='http://127.0.0.1:3000')
def go():
    print("----------------------------GO--------------------------------")
    print("Current uuid: ", session.get('uuid'))
    response_dict = {"Created": False, "Name" : "", "Error" : "", "when" : ""}
    data = request.json
    weather_main = data['main']
    weather_description = data['description']
    temperature = data['temperature']

    if weather_main == None or weather_description == None or temperature == None:
        print("Your Post was probs missing some parameters")
        weather_main = "Drizzle"
        weather_description = "drizzle"
        temperature = 278 # in kelvin

    try:
        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = creds.SPOTIFY_ID, client_secret = creds.SPOTIFY_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE, cache_handler=cache_handler)
    except TypeError as e:
        response['Error'] = "Error in getting session cache path"
        return response
    
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        response_dict['Error'] = "Error in getting valid token, sent back"
        return response_dict

    sp = spotipy.Spotify(auth_manager=sp_oauth)
    spotify_user_id = sp.me()['id']
    
    # Check if user is in system
    in_system = False
    cursor = mysql.connection.cursor() 
    cursor.execute("SELECT user_id FROM user_dates WHERE user_id = %s LIMIT 1;", [spotify_user_id])
    if len(cursor.fetchall()) > 0:
        in_system = True
    cursor.close()
    
    # If user is in system, songs are already in database
    # If user is not in system
    print("User in Databse: ", in_system)
    if not in_system:
        tracks = []
        songs_to_add = []
        
        for off in range(0, 10000, 50):
            print(off)
            response = sp.current_user_saved_tracks(limit=50,offset=off,market="US")
            if response == None:
                break
            cur_tracks = [x['track'] for x in response['items']]
            new_ids = [x['id'] for x in cur_tracks]
               
            tracks.extend(new_ids)
            feats = sp.audio_features(new_ids)
            
            none_indicies = [i for i in range(len(feats)) if feats[i] == None]
            if len(none_indicies) > 0:
                print("At least one song present that does not have spotify features")
                response_dict["Error"] = "Error in getting at least one song's spotify features"
                # Not returning response_dict because program could still mostly succeed
            cur_tracks = [t for i, t in enumerate(cur_tracks) if i not in none_indicies]
            feats = [f for i, f in enumerate(feats) if i not in none_indicies]
            
            
            songs_to_add.extend([tuple([cur_tracks[x]['id'], cur_tracks[x]['name'], cur_tracks[x]['album']['artists'][0]['name'], 
                                feats[x]['energy'], feats[x]['tempo'], feats[x]['danceability'], feats[x]['loudness'],
                                feats[x]['valence'], feats[x]['instrumentalness']]) for x in range(len(cur_tracks))])
            if len(response['items']) < 50:
                break
        
        #Creating a connection cursor
        cursor = mysql.connection.cursor()
        sql = """INSERT IGNORE INTO song_stats 
        (song_id,name,artist,energy,tempo,danceability,loudness,valence,instrumentalness)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        cursor.executemany(sql, songs_to_add)
        sql2 = "INSERT IGNORE INTO user_songs (song_id,user_id) VALUES (%s, %s);"
        cursor.executemany(sql2, [[x, spotify_user_id] for x in tracks])
        
        try:
            #Saving the Actions performed on the DB
            mysql.connection.commit()
            #Closing the cursor
            cursor.close()
        except:
            print("Error in adding songs to database")
            response_dict["Error"] = "Error in adding liked songs to database"
            return response_dict
        
    # Update User Access Time
    cursor = mysql.connection.cursor()
    user_dates_sql = "INSERT IGNORE INTO user_dates (user_id, datetime_accessed) VALUES(%s, now()) ON DUPLICATE KEY UPDATE datetime_accessed=now()"
    print(spotify_user_id)
    cursor.execute(user_dates_sql, [spotify_user_id])
    try:
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()
    except:
        print("Error in commiting")
        response_dict["Error"] = "Error in commiting new user update time"
        return response_dict
    
    cursor = mysql.connection.cursor()
    # Get user liked songs population statistics
    get_stats_sql = """SELECT AVG(tempo) AS tempo_avg, STD(tempo) AS tempo_std, 
        AVG(energy) as energy_avg, STD(energy) as energy_std, 
        AVG(valence) AS valence_avg, STD(valence) AS valence_std
        FROM song_stats 
        WHERE song_id IN (SELECT song_id FROM user_songs WHERE user_id = %s);"""
    cursor.execute(get_stats_sql, [spotify_user_id])
    row = cursor.fetchone()
    if not (row == None or len(row) == 0 or row[0] == None):
        row_headers=[x[0] for x in cursor.description]
        user_pop_stats = dict(zip(row_headers, [round(float(x),3) for x in row]))
        print("Collected Stats: ", user_pop_stats)
    else:
        print("Error in getting songs of user, returned no songs")
        response_dict["Error"] = "Error in getting liked songs statistics"
        return response_dict
    
    # Execute sql to get custom playlist
    custom_sql_left = "SELECT song_id FROM song_stats WHERE song_id IN (SELECT song_id FROM user_songs WHERE user_id = %s) AND "
    custom_sql = custom_sql_left + get_custom_playlist_sql(main_weather=weather_main, 
                                                            description_weather=weather_description, temp=temperature, 
                                                            user_pop_stats=user_pop_stats) + ";"
    cursor.execute(custom_sql, [spotify_user_id])
    custom_ids = [x[0] for x in cursor.fetchall()]
    cursor.close()
    
    playlist_name = "Weatherify Test Playlist (Temp={0}) (Main={1}) (Desc={2})".format(temperature, weather_main, weather_description)
    playlists = [p['name'] for p in sp.user_playlists(user=spotify_user_id)['items']]
    if playlist_name not in playlists:
        sp.user_playlist_create(user=spotify_user_id, name=playlist_name)
        
    playlists = [(p['name'], p['id']) for p in sp.user_playlists(user=spotify_user_id)['items']]
    for playlist in playlists:
        if playlist[0] == playlist_name:
            sp.user_playlist_replace_tracks(user=spotify_user_id, playlist_id=playlist[1], tracks=custom_ids[:100])
            for off in range(100, len(custom_ids), 100):
                sp.user_playlist_add_tracks(user=spotify_user_id, playlist_id=playlist[1], tracks=custom_ids[off:off+100])
            break
    print("Playlist Created: ", playlist_name, " for ", spotify_user_id)
    print("----------------------------END OF GO---------------------------------------------")
    response_dict["Created"] = True
    response_dict["Name"] = playlist_name
    response_dict['when'] = str(arrow.now().format('YYYY-MM-DD HH:mm:ss'))
    return response_dict

# Get user information out of table
@app.route("/api/out", methods=['GET'])
def remove_info():
    print("---------------------------------------------OUT--------------------------------")
    response = {"logged_out" : False}
    try:
        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = creds.SPOTIFY_ID, client_secret = creds.SPOTIFY_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE, cache_handler=cache_handler)
    except TypeError as e:
        session.clear()
        print("could not find session cache path on logout")
        response['logged_out'] = True
        return response
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        print("Spotify User not signed in, only clearing session data")
        try:
            os.remove(session_cache_path())
            session.clear()
        except OSError as e:
            print ("Error: %s - %s." % (e.filename, e.strerror))
            print("---------------------------------------------END OF OUT--------------------------------")
        except TypeError as e:
            session.clear()
        response['logged_out'] = True
        print("---------------------------------------------END OF OUT--------------------------------")
        return response
    sp = spotipy.Spotify(auth_manager=sp_oauth)

    spotify_user_id = sp.me()['id']
    print(spotify_user_id)
    #Creating a connection cursor
    cursor = mysql.connection.cursor()
    sql = """DELETE FROM user_dates WHERE user_id = %s;"""
    cursor.execute(sql, [spotify_user_id])
    try:
        #Saving the Actions performed on the DB
        mysql.connection.commit()
    except:
        print("error in removing user from user_dates")
    sql = """DELETE FROM user_songs WHERE user_id = %s;"""
    cursor.execute(sql, [spotify_user_id])
    
    try:
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()
    except:
        print("Error in removing user info from users")   
    try:
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
        
    response['logged_out'] = True
    print("---------------------------------------------END OF OUT--------------------------------")
    return response


# Generates the second half of the SQL statement for song parameters based on weather description
def get_custom_playlist_sql(main_weather: str, description_weather: str, temp: int,
                            user_pop_stats: dict) -> str:
    """
    dict user_pop_stats : tempo_avg, tempo_std, energy_avg, energy_std, valence_avg, valence_std
    """
    # Set default values (will get all songs)
    tempo_lower = 0
    tempo_upper = 9999
    energy_lower = 0
    energy_upper = 1
    valence_lower = 0
    valence_upper = 1
    
    # Get statistics from sent dictionary
    tempo_avg = user_pop_stats['tempo_avg']
    tempo_std = user_pop_stats['tempo_std']
    energy_avg = user_pop_stats['energy_avg']
    energy_std = user_pop_stats['energy_std']
    valence_avg = user_pop_stats['valence_avg']
    valence_std = user_pop_stats['valence_std']
    
    # Get tempo parameters based on temperature
    if temp <= 272:
        tempo_upper = tempo_avg - tempo_std
    elif temp >= 300:
        tempo_lower = tempo_avg + tempo_std
    else:
        tempo_lower_int = tempo_avg - tempo_std
        tempo_cent = (tempo_std * (300 - temp) / 14)  + tempo_lower_int
        tempo_lower = tempo_cent - 0.5*tempo_std
        tempo_upper = tempo_cent + 0.5*tempo_std
    
    tempo_str = "tempo >= {0} AND tempo <= {1}".format(tempo_lower, tempo_upper)

    # Get energy and valence parameters based on weather
    # Not so great outside weather
    if main_weather in ["Drizzle", "Haze", "Fog", "Dust", "Mist"] or description_weather in ["light rain", "moderate rain", "light snow", "Snow", "Sleet", "overcast clouds: 85-100%"]:
        energy_lower = energy_avg - energy_std
        energy_upper = energy_avg
        valence_upper = valence_avg
        valence_lower = valence_avg - valence_std
        
    # Stormy!!!
    elif main_weather in ["Thunderstorm", "Rain", "Snow", "Squall", "Sand", "Ash"]:
        energy_upper = energy_avg - energy_std * 0.5
        valence_upper = valence_avg - 0.4*valence_std
    
    # Regular
    else:
        energy_lower = energy_avg
        valence_lower = valence_avg

    return tempo_str + " AND energy >= {0} AND energy <= {1} AND valence >= {2} AND valence <= {3}".format(energy_lower, energy_upper, valence_lower, valence_upper)

# For testing multiple users
@app.route('/api/current_user')
def current_user():
    print("----------------------CURRENT USER--------------------------------")
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id = creds.SPOTIFY_ID, client_secret = creds.SPOTIFY_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE, cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        print("failed to get current user")
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    cur_id = spotify.me()['id']
    print("Current User: ", cur_id)
    print("----------------------END OF CURRENT USER--------------------------------")
    response_dict = {"Status" : cur_id}
    return response_dict

# For testing multiple users
@app.route('/api/get_5_days')
def get_days():
    print("----------------------Start Get 5 Days--------------------------------")
    response = {"days": wa.get_5_days()}
    print("----------------------End Get 5 Days--------------------------------")
    return response
    

if __name__ == "__main__":
    app.run(host='127.0.0.1', threaded=True, debug=True, port=1000)