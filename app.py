from flask import Flask
from flask_sock import Sock
from twilio.rest import Client
import os
import json
import time

app = Flask(__name__)
sock = Sock(app)

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_FROM")
TO_NUMBER = os.getenv("CLIENT_NUMBER")

client = Client(TWILIO_SID, TWILIO_TOKEN)

GAS_THRESHOLD = 350
WEIGHT_THRESHOLD = 2.0

last_alert_time = 0
ALERT_COOLDOWN = 300

def send_sms(msg):
    try:
        client.messages.create(
            body=msg,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )
        print("SMS Sent Successfully")
    except Exception as e:
        print("SMS Failed:", e)

@sock.route('/ws')
def websocket(ws):

    print("ESP8266 Connected")

    global last_alert_time

    while True:
        data = ws.receive()

        print("Raw Data:", data)

        try:
            payload = json.loads(data)
        except:
            print("Invalid JSON")
            continue

        gas = payload.get("gas", 0)
        fire = payload.get("fire", False)
        weight = payload.get("weight", 0)
        device = payload.get("device_id", "Unknown")

        alert = False
        msg = f"Alert from {device}\n"

        if gas > GAS_THRESHOLD:
            msg += "Gas Leak Detected\n"
            alert = True

        if fire:
            msg += "Fire Detected\n"
            alert = True

        if weight < WEIGHT_THRESHOLD:
            msg += "Low Cylinder Level\n"
            alert = True

        current = time.time()

        if alert and (current - last_alert_time) > ALERT_COOLDOWN:
            send_sms(msg)
            last_alert_time = current

@app.route('/')
def home():
    return "Server is running...."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
