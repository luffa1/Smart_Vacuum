import smtplib
import threading
import time
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
import jwt
from flask import Flask, request, jsonify
from flask_talisman import Talisman

# ---- CONFIGURATION ----
EMAIL_SENDER = "your-email@example.com"
RECIPIENT_EMAIL = "your-recipient-email@example.com"
EMAIL_USERNAME = "your-username"
EMAIL_PASSWORD = "your-app-password"
SMTP_SERVER = "smtp.mailtrap.io"
SMTP_PORT = 2525
SECRET_KEY = "SuperSecretKey"
TOKEN_EXPIRATION_HOURS = 1

# ---- SMART VACUUM CLASS ----
class SmartVacuum:
    def __init__(self):
        self.is_cleaning = False
        self.battery_level = 100
        self.cleaning_history = []
        self.status = "Idle"

    def start_cleaning(self):
        if self.battery_level < 20:
            self.status = "Battery too low to start cleaning."
            return False
        self.is_cleaning = True
        self.status = "Cleaning in progress."
        self.log_event("Started cleaning")
        self.notify("Vacuum started cleaning.")
        return True

    def stop_cleaning(self):
        if self.is_cleaning:
            self.is_cleaning = False
            self.status = "Cleaning completed."
            self.log_event("Finished cleaning")
            self.notify("Vacuum finished cleaning.")

    def continue_cleaning(self):
        if self.start_cleaning():  # Start cleaning again
            self.notify("Continuing cleaning")
            threading.Thread(target=self.simulate_cleaning).start()

    def encounter_problem(self, problem):
        self.status = f"Problem encountered: {problem}"
        self.log_event(self.status)
        self.notify(self.status)
        self.is_cleaning = False

    def dock(self):
        self.status = "Docking and charging."
        self.battery_level = 100
        self.log_event("Docked and recharged")
        self.notify("Vacuum docked and recharged.")

    def simulate_cleaning(self):
        for _ in range(10):  # Simulate 5 cleaning cycles
            if not self.is_cleaning:
                break
            time.sleep(5)
            self.battery_level -= 2
            if self.battery_level < 10:
                self.encounter_problem("Battery critically low.")
                break

        if self.is_cleaning:
            self.stop_cleaning()
            self.dock()

    def log_event(self, event):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cleaning_history.append({"event": event, "timestamp": timestamp})

    def notify(self, message):
        send_email(f"Vacuum Notification", message, RECIPIENT_EMAIL)

# ---- EMAIL NOTIFICATION FUNCTION ----
def send_email(subject, body, to_email):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# ---- JWT AUTHENTICATION ----
def generate_token():
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc)
    }
    print(f"SECRET_KEY used for encoding: {SECRET_KEY}")
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.DecodeError:
        return False

# ---- FLASK WEB INTERFACE ----
app = Flask(__name__)
Talisman(app)  # Enable HTTPS
vacuum = SmartVacuum()

@app.before_request
def authenticate():
    if request.endpoint not in ['get_token', 'home']:
        token_header = request.headers.get("Authorization")
        if not token_header or " " not in token_header:
            return jsonify({"error": "Unauthorized"}), 401

        token = token_header.split(" ")[1]
        if not verify_token(token):
            return jsonify({"error": "Unauthorized"}), 401

@app.route('/')
def home():
    return "<h1>Smart Vacuum Controller</h1><p>Use the API endpoints to control your vacuum.</p>"

@app.route('/get_token', methods=['GET'])
def get_token():
    return jsonify({"token": generate_token()}), 200

@app.route('/start', methods=['POST'])
def start_cleaning():
    if vacuum.start_cleaning():
        threading.Thread(target=vacuum.simulate_cleaning).start()
        return jsonify({"message": "Vacuum started cleaning."}), 200
    return jsonify({"message": vacuum.status}), 400

@app.route('/stop', methods=['POST'])
def stop_cleaning():
    vacuum.stop_cleaning()
    return jsonify({"message": "Vacuum stopped cleaning."}), 200

@app.route('/continue', methods=['POST'])
def continue_cleaning():
    vacuum.continue_cleaning()
    return jsonify({"message": "Vacuum is continuing cleaning."}), 200

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({"status": vacuum.status, "battery": vacuum.battery_level}), 200

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(vacuum.cleaning_history), 200

@app.route('/simulate_problem', methods=['POST'])
def simulate_problem():
    data = request.json
    problem = data.get("problem", "Unknown problem")
    vacuum.encounter_problem(problem)
    return jsonify({"message": f"Simulated problem: {problem}"}), 200

# ---- SCHEDULED CLEANING ----
def schedule_cleaning():
    while True:
        now = datetime.now()
        if now.hour == 9:  # Example: start cleaning every day at 9 AM
            vacuum.start_cleaning()
            vacuum.simulate_cleaning()
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=schedule_cleaning, daemon=True).start()
    app.run(ssl_context=("cert.pem", "key.pem"), debug=True)  # Run with HTTPS

