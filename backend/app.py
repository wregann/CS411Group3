from multiprocessing.sharedctypes import Value
import weather_access as wa
import spotify_access as sa
import creds
from flask import Flask, render_template, redirect, request, session, make_response,session,redirect
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS #comment this on deployment
import time
import spotipy
import json
import os
from flask_mysqldb import MySQL





app = Flask(__name__, template_folder="../templates")
CORS(app)
app.config['MYSQL_HOST'] = creds.DB_HOSTNAME
app.config['MYSQL_USER'] = creds.DB_USERNAME
app.config['MYSQL_PASSWORD'] = creds.DB_PASSWORD
app.config['MYSQL_DB'] = "WeatherifyDB"
 
mysql = MySQL(app)
#CORS(app) #comment this on deployment
#api = Api(app)
app.secret_key = creds.APP_SECRET
API_BASE = 'https://accounts.spotify.com'
REDIRECT_URI = "http://127.0.0.1:1000/spotify_callback"

SCOPE = 'playlist-modify-private,playlist-modify-public,ugc-image-upload,user-library-read'


@app.route("/main")
def serve():
    return render_template('example.html', value=wa.get_5_days())

@app.route("/get_weather_data/<city_string>", methods = ['GET'])
def get_weather_data(city_string):
    try:
        lat, lon = wa.get_lat_lon_from_input(key=creds.OPENWEATHER_KEY, city=city_string)
    except ValueError as e:
        print(e)
        return 'Error: Could not get city longitude and latitude, please try agian'
    
    try:
        five_day_data_dict = wa.get_5_day_data(key=creds.OPENWEATHER_KEY, lat=lat, lon=lon)
    except ValueError as e:
        print(e)
        return 'Error: could not get weather data from latitude and lognitude'
    
    return five_day_data_dict

# authorization-code-flow Step 1. Have your application request authorization; 
# the user logs in and authorizes access
@app.route("/spotify_login")
def verify():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = creds.SPOTIFY_ID, client_secret = creds.SPOTIFY_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)

# authorization-code-flow Step 2.
# Have your application request refresh and access tokens;
# Spotify returns access and refresh tokens
@app.route("/spotify_callback")
def api_callback():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = creds.SPOTIFY_ID, client_secret = creds.SPOTIFY_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    # Saving the access token along with all other token related info
    session["token_info"] = token_info


    return redirect("/main")

# authorization-code-flow Step 3.
# Use the access token to access the Spotify Web API;
# Spotify returns requested data
@app.route("/go", methods=['POST', 'GET'])
def go():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')
    data = request.form
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    spotify_username = sp.me()['id']
    
    # Check if user is in system
    in_system = False
    cursor = mysql.connection.cursor() 
    cursor.execute("SELECT username FROM users WHERE username = %s LIMIT 1;", [spotify_username])
    if len(cursor.fetchall()) > 0:
        in_system = True
    try:
        #Closing the cursor
        cursor.close()
    except:
        print("Error in getting Spotify Username")
    
    # If user is in system, songs are already in database
    # If user is not in system
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
            songs_to_add.extend([tuple([cur_tracks[x]['id'], cur_tracks[x]['name'], cur_tracks[x]['album']['artists'][0]['name'], 
                                feats[x]['energy'], feats[x]['tempo'], feats[x]['danceability'], feats[x]['loudness'],
                                feats[x]['valence'], feats[x]['speechiness'], feats[x]['liveness'], 
                                feats[x]['instrumentalness'], feats[x]['duration_ms'], feats[x]['key']]) for x in range(len(cur_tracks))])
            if len(response['items']) < 50:
                break
        
        #Creating a connection cursor
        cursor = mysql.connection.cursor()
        sql = """INSERT IGNORE INTO songs 
        (id,name,artist,energy,tempo,danceability,loudness,valence,speechiness,liveness,instrumentalness,duration_ms,song_key)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        cursor.executemany(sql, songs_to_add)
        sql2 = "INSERT IGNORE INTO users (id,username) VALUES (%s, %s);"
        cursor.executemany(sql2, [[x, spotify_username] for x in tracks])
        try:
            #Saving the Actions performed on the DB
            mysql.connection.commit()
            #Closing the cursor
            cursor.close()
        except:
            print("Error in adding songs to database")
    
    print("In System: " + str(in_system))
    
    # Create custom playlist
    cursor = mysql.connection.cursor()
    custom_sql_left = "SELECT id FROM songs WHERE id IN (SELECT id FROM users WHERE username = %s) AND "
    custom_sql = custom_sql_left + get_custom_playlist_sql("", "") + ";"
    cursor.execute(custom_sql, [spotify_username])
    custom_ids = [x[0] for x in cursor.fetchall()]
    try:
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()
    except:
        print("Error in getting song custom id selection from database")
    
    playlist_name = "Weatherify Test Playlist"
    playlists = [p['name'] for p in sp.user_playlists(user=spotify_username)['items']]
    if playlist_name not in playlists:
        sp.user_playlist_create(user=spotify_username, name=playlist_name)
        
    playlists = [(p['name'], p['id']) for p in sp.user_playlists(user=spotify_username)['items']]
    for playlist in playlists:
        if playlist[0] == playlist_name:
            sp.user_playlist_replace_tracks(user=spotify_username, playlist_id=playlist[1], tracks=custom_ids[:100])
            for off in range(100, len(custom_ids), 100):
                sp.user_playlist_add_tracks(user=spotify_username, playlist_id=playlist[1], tracks=custom_ids[off:off+100])
            break
    
    return redirect("main")

# Get user information out of table
@app.route("/out", methods=['GET'])
def remove_info():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    spotify_user_id = sp.me()['id']
    #Creating a connection cursor
    cursor = mysql.connection.cursor()
    sql = """DELETE FROM users WHERE username = %s;"""
    cursor.execute(sql, [spotify_user_id])
    try:
        #Saving the Actions performed on the DB
        mysql.connection.commit()
        #Closing the cursor
        cursor.close()
    except:
        print("Error in removing user info from users")
        
    return redirect("main")
    
def get_custom_playlist_sql(main_weather: str, description_weather: str):
    return "energy > 0.75"




# Checks to see if token is valid and gets a new token if not
def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = creds.SPOTIFY_ID, client_secret = creds.SPOTIFY_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE)
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid



if __name__ == "__main__":
    app.run(port=1000, debug=True)