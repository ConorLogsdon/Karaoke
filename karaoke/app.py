from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import requests
import base64
import os
import qrcode
from io import BytesIO
import random

app = Flask(__name__)

song_queue = []

@app.route("/qr")
def qr_code():
    request_url = request.host_url.strip("/") + "/"
    
    qr = qrcode.make(request_url)
    img_io = BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

# config Spotify client ID/Secret
SPOTIFY_CLIENT_ID = os.environ.get("")
SPOTIFY_CLIENT_SECRET = os.environ.get("")
SPOTIFY_TOKEN = None

def get_spotify_token():
    global SPOTIFY_TOKEN
    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}"
    }
    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    response.raise_for_status()
    SPOTIFY_TOKEN = response.json()["access_token"]

@app.route('/')
def index():
    popular_songs = ["Bohemian Rhapsody", "Shake It Off", "Sweet Caroline", "Uptown Funk", "Let It Go", "Mr. Brightside"]
    song_of_the_day = random.choice(popular_songs)  # Randomly selects a song from the list
    return render_template('index.html', song_of_the_day=song_of_the_day)

def get_spotify_suggestions(query):
    if not SPOTIFY_TOKEN:
        get_spotify_token()

    headers = {
        "Authorization": f"Bearer {SPOTIFY_TOKEN}"
    }

    params = {
        "q": query,
        "type": "track",
        "limit": 5
    }

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    if response.status_code == 401:
        get_spotify_token()
        return get_spotify_suggestions(query)

    tracks = response.json().get("tracks", {}).get("items", [])
    return [f"{t['name']} – {t['artists'][0]['name']}" for t in tracks]

@app.route("/autocomplete")
def autocomplete():
    query = request.args.get("q", "").lower()
    suggestions = get_spotify_suggestions(query)
    return jsonify(suggestions)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/request", methods=["POST"])
def request_song():
    name = request.form.get("name")
    song_name = request.form.get("song")

    if song_name:
        song_entry = {"name": name, "song": song_name}
        song_queue.append(song_entry)
        return redirect(url_for("view_queue"))
    else:
        return redirect(url_for("home"))

@app.route("/queue")
def view_queue():
    return render_template("queue.html", queue=song_queue)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
