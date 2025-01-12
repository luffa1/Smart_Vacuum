# Smart_Vacuum
# Smart Vacuum Controller

This project is a Flask-based IoT application to control a simulated smart vacuum cleaner with integrated email notifications, JWT-based authentication, and a secured HTTPS connection.

---

## Features

1. **Smart Vacuum Simulation**
   - Start, stop, and dock the vacuum.
   - Handle problems like low battery.
   - Log cleaning events with timestamps.

2. **Secure Communication**
   - HTTPS encryption using a local SSL certificate.
   - JWT-based authentication for API endpoints.

3. **Email Notifications**
   - Get notified about the vacuum's actions (start, stop, docking, or issues).

4. **Web API**
   - Interact with the vacuum using RESTful API endpoints.

5. **History Logging**
   - Retrieve a log of cleaning events.

6. **Scheduled Cleaning**
   - Automatically starts cleaning every day at 9 AM.

---

## Installation

### Prerequisites
- Python 3.10 or higher
- Flask
- Flask-Talisman
- pyjwt
- Mailtrap account (for testing emails)

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd smart-vacuum
   ```

2. **Install dependencies:**
   ```bash
   pip install flask flask-talisman pyjwt
   ```

3. **Generate SSL certificates:**
   ```bash
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

   Place `cert.pem` and `key.pem` in the project directory.

4. **Configure email settings:**
   Update the following variables in `smart_vacuum.py`:
   ```python
   EMAIL_SENDER = "your-email@example.com"
   EMAIL_PASSWORD = "your-app-password"
   SMTP_SERVER = "smtp.mailtrap.io"  # Or your preferred SMTP server
   SMTP_PORT = 2525  # Port for Mailtrap
   ```

5. **Run the application:**
   ```bash
   python smart_vacuum.py
   ```

6. **Access the application:**
   Open `https://127.0.0.1:5000` in your browser.

---

## API Endpoints

### Authentication
- **GET `/get_token`**
  - Generate a JWT token for authenticated requests.

### Vacuum Operations
- **POST `/start`**
  - Start vacuum cleaning.
- **POST `/stop`**
  - Stop vacuum cleaning.
- **POST `/continue`**
  - Resume vacuum cleaning.
- **POST `/simulate_problem`**
  - Simulate a problem (e.g., "Obstacle detected").

### Status and History
- **GET `/status`**
  - Get the vacuum's current status and battery level.
- **GET `/history`**
  - Retrieve the cleaning history.

---

## Testing

### 1. Using Postman or cURL

- Example to start cleaning:
  ```bash
  curl -X POST https://127.0.0.1:5000/start -H "Authorization: Bearer <your-token>"
  ```

- Example to simulate a problem:
  ```bash
  curl -X POST https://127.0.0.1:5000/simulate_problem -H "Authorization: Bearer <your-token>" -H "Content-Type: application/json" -d '{"problem": "Obstacle detected"}'
  ```

### 2. Testing Email Notifications

Check your email (configured in `EMAIL_SENDER` and `RECIPIENT_EMAIL`) to verify notifications for:
- Cleaning start
- Cleaning stop
- Encountered problems

---

