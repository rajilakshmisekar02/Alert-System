from flask import Flask
from flask_socketio import SocketIO
from twilio.rest import Client
import os
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_FROM")
TO_NUMBER = os.getenv("CLIENT_NUMBER")

if not TWILIO_SID or not TWILIO_TOKEN or not FROM_NUMBER or not TO_NUMBER:
    print("⚠️ TWILIO ENV VARIABLES MISSING!")

client = Client(TWILIO_SID, TWILIO_TOKEN)

GAS_THRESHOLD = 350
WEIGHT_THRESHOLD = 2.0

last_alert_time = 0
ALERT_COOLDOWN = 300   # 5 minutes


def send_sms(msg):
    try:
        client.messages.create(
            body=msg,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )
        print("SMS Sent Successfully")
    except Exception as e:
        print("SMS Sending Failed:", e)


@socketio.on('connect')
def connected():
    print("Device Connected")


@socketio.on('message')
def handle_message(data):

    global last_alert_time

    gas = data.get("gas", 0)
    fire = data.get("fire", False)
    weight = data.get("weight", 0)
    device = data.get("device_id", "Unknown Device")

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

    print("Data Received:", data)


@socketio.on('disconnect')
def disconnected():
    print("Device Disconnected")


@app.route('/')
def hello_world():
    return 'Server is running....'


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080)
