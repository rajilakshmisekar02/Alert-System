from flask import Flask, request, jsonify
from twilio.rest import Client
import os
import time

app = Flask(__name__)

# Twilio Config
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_FROM")
TO_NUMBER = os.getenv("CLIENT_NUMBER")

client = Client(TWILIO_SID, TWILIO_TOKEN)

GAS_THRESHOLD = 350
WEIGHT_THRESHOLD = 2.0

last_alert_time = 0
ALERT_COOLDOWN = 120   # 5 minutes


def send_sms(msg):
    try:
        client.messages.create(
            body=msg,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )
        print("SMS Sent")
    except Exception as e:
        print("SMS Error:", e)
    print(f'alert {msg}')


@app.route('/')
def home():
    return "Alert System Running........"

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"server": "online"})

@app.route('/data', methods=['POST'])
def receive_data():
    global last_alert_time

    data = request.get_json()
    print("Received:", data)

    gas = data.get("gas", 0)
    fire = data.get("fire", False)
    weight = data.get("weight", 0)
    device = data.get("device_id", "ESP8266")

    alert = False

    msg = f"Alert from {device}\n\n"
    msg += f"Gas Level: {gas}\n"
    msg += f"Fire Status: {'YES' if fire else 'NO'}\n"
    msg += f"Weight Level: {weight} kg\n\n"

    if gas > GAS_THRESHOLD:
        msg += "⚠ Gas Leak Detected\n"
        alert = True

    if fire:
        msg += "🔥 Fire Detected\n"
        alert = True

    if weight < WEIGHT_THRESHOLD:
        msg += "⚠ Low Cylinder Level\n"
        alert = True

    current = time.time()

    if alert and (current - last_alert_time) > ALERT_COOLDOWN:
        send_sms(msg)
        last_alert_time = current

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
