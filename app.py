from twilio.rest import Client
import os
import time
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
# cors_allowed_origins="*" is important for external devices like ESP32
# socketio = SocketIO(app, cors_allowed_origins="*")
# In your app.py
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

@app.route('/')
def index():
    return "WebSocket Server is Running!"

# This function runs when the ESP32 sends a message
@socketio.on('pot_data')
def handle_pot_value(data):
    print(f"Potentiometer Value received: {data}")

if __name__ == '__main__':
    # Use '0.0.0.0' so it's accessible over the internet
    socketio.run(app, host='0.0.0.0', port=5000)
