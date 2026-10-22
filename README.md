# Privyr Webhook & AI Lead Router

A FastAPI-powered backend service that receives real-time webhook events from **Privyr CRM**, generates professional, context-aware initial response email drafts using **Google Gemini AI**, and automatically routes lead notifications via **SMTP (Gmail)** to your internal team.

---

## 🚀 Features

- **Privyr Webhook Integration**: Ingests lead events (such as `CLIENT_CREATED`) directly from Privyr.
- **AI-Powered Draft Generation**: Generates customized, professional first-response email subjects and bodies tailored to client inquiry notes using Google Gemini.
- **Resilient AI Pipeline**: Supports primary and fallback Gemini models (e.g., handling 503 service unavailabilities gracefully).
- **Automated Email Dispatch**: Sends notifications containing both the AI draft and the lead's contact details via SMTP with TLS encryption.
- **Secure Authentication**: Validates incoming webhook requests with constant-time Bearer token comparison (`PRIVYR_WEBHOOK_SECRET`).
- **Observability & Metrics**: Tracks execution latency across Gemini generation, SMTP delivery, and total request lifecycle.

---

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)
- **AI Engine**: [Google GenAI SDK](https://github.com/googleapis/python-genai) (`google-genai`)
- **Email Protocol**: Python standard library `smtplib` + `email.message` (TLS enabled)
- **Dependency Management**: [Poetry](https://python-poetry.org/)
- **Python Version**: 3.12

---

## 📁 Project Structure

```text
privyr-webhook/
├── src/
│   ├── __init__.py
│   ├── config.py        # Centralized Pydantic application settings
│   ├── main.py          # FastAPI application initialization
│   └── mail/
│       ├── __init__.py
│       ├── helper.py    # Asynchronous SMTP email sender
│       ├── model.py     # Pydantic schemas (PrivyrWebhook, EmailDraft)
│       ├── router.py    # Webhook endpoint route handlers
│       └── services.py  # Gemini generation & email dispatch services
├── .env.example         # Template for required environment variables
├── pyproject.toml       # Project metadata & dependencies
├── poetry.lock          # Locked dependency versions
└── README.md            # Project documentation
```

---

## ⚙️ Prerequisites

- **Python 3.12** installed on your system.
- **Poetry** installed (`pip install poetry`) or `uv`.
- A **Google Gemini API Key** (obtainable from [Google AI Studio](https://aistudio.google.com/)).
- An **SMTP-enabled email account** (e.g., a Gmail account with an [App Password](https://myaccount.google.com/apppasswords)).

---

## 📦 Installation & Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd privyr-webhook
```

### 2. Install dependencies

Using Poetry:
```bash
poetry install
```

### 3. Configure environment variables

Copy the example environment file:
```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

Fill in your actual credentials in `.env`:

```ini
# Privyr Webhook Authentication (Bearer Token)
PRIVYR_WEBHOOK_SECRET=your_privyr_webhook_bearer_token_here

# Google Gemini AI Configuration
GEMINI_API_KEY=your_google_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
GEMINI_FALLBACK_MODEL=gemini-2.5-flash

# Company Configuration (Used by Gemini for email drafts)
COMPANY_SERVICES="Describe your company services, e.g., UAE Company Formation, Accounting & Tax, Visa Services"

# SMTP / Email Server Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_app_specific_password_here
SMTP_USE_TLS=true
DEFAULT_SENDER_EMAIL=your_email@example.com

# Notification Recipient
IT_TEAM_EMAIL=team_notifications@example.com
```

---

## 🚦 Running the Application

### Development Server

Run the server with hot-reloading:

```bash
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The service will be accessible at:
- **API Base URL**: `http://localhost:8000`
- **Swagger UI Documentation**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

---

## 📡 API Reference

### 1. Health Check
Checks if the service is live.

- **URL**: `/`
- **Method**: `GET`
- **Response**:
```json
{
  "status": "ok",
  "service": "privyr-webhook"
}
```

---

### 2. Privyr Webhook Endpoint
Processes incoming Privyr lead events.

- **URL**: `/webhooks/privyr`
- **Method**: `POST`
- **Headers**:
  - `Content-Type: application/json`
  - `Authorization: Bearer <PRIVYR_WEBHOOK_SECRET>`

#### Example Request Body (`CLIENT_CREATED`):
```json
{
  "event_type": "CLIENT_CREATED",
  "client": {
    "name": "Rahul Sharma",
    "email": "rahul.sharmas@example.com",
    "notes": "Looking for UAE company incorporation and visa process"
  }
}
```

#### Example Response:
```json
{
  "success": true,
  "event_type": "CLIENT_CREATED",
  "recipient": "team_notifications@example.com",
  "subject": "UAE Company Incorporation Inquiry - kitaab.ai",
  "body": "Hi Rahul,\n\nThank you for reaching out to kitaab.ai...\n\n--- Lead Contact Details ---\nClient Name: Rahul Sharma\nClient Email: rahul.sharmas@example.com\n",
  "email_status": "sent",
  "message": "AI-generated lead notification sent to the IT team"
}
```

---

## 🔗 Connecting to Privyr

1. Expose your local port (using tools like [ngrok](https://ngrok.com/) or [Cloudflare Tunnels](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)):
   ```bash
   ngrok http 8000
   ```
2. In your Privyr account:
   - Navigate to **Integrations / Webhooks**.
   - Set the Webhook URL to: `https://your-domain.ngrok-free.app/webhooks/privyr`
   - Set the authorization header / Bearer token matching your `PRIVYR_WEBHOOK_SECRET`.
   - Enable the **Client Created** trigger.

---

## 🛡️ License

This project is proprietary and intended for internal operations.
