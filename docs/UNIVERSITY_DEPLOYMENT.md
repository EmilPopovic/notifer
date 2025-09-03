# 📚 NotiFER - University Deployment & Integration Guide

## Overview

**NotiFER** is a production-ready, open-source notification system for FER students.
It automatically monitors official FER iCal calendars and sends timely email notifications about timetable changes.
NotiFER is designed for easy, secure deployment by university IT and includes a robust API for administrative management.

---

## 🎯 Benefits for FER

- **Improved Communication:** Studetns are instantly notified of schedule changes, reducing confusion and missed classes and exams.
- **Administrative Control:** FER staff or automated systems can securely manage subscriptions, pause/resume notifications, and query status via a protected API.
- **Privacy & Security:** No unnecessary data is collected. All sensitive operations require secure API tokens or email confirmation. GDPR-friendly.
- **Open Source:** FER can audit, adapt, and extend the codebase as needed.

---

## 🏗️ System Architecture

- **Backend:** Python (FastAPI), SQLite
- **Frontend:** Responsive, accessible web UI (HTML/CSS/JS)
- **Email:** Uses SMTP or transactional email provider (configurable), Jinja2 templates
- **Deployment:** Docker Compose for easy setup

## 🚀 Deployment Instructions

### 1. Prerequisites

- Docker & Docker Compose installed
- SMTP credentials for sending emails

### 2. Quick Start

```bash
git clone https://github.com/myolnyr/NotiFER.git
cd NotiFER
cp .env.example .env
# Edit .env and config/app.conf with your settings (see below)
docker compose up -d
```

### 3. Configuration

- **.env:**
    Set needed credentials and API token hash (SHA-256 of your chosen secret token),

- **config/app.conf**
    Set email method and worker preferences.

### 4. Reverse Proxy (Recommended)

Run behind Nginx/Apache for HTTPS and domain routing.
Expose port 8026 internally.

---

## 🔑 Admin API

All endpoints require a secure Bearer token (hash stored in `.env`).

### Example Endpoints

- **Add subscription by calendar URL:**
    `POST /uni/subscribe/url`
- **Add subscription by username/auth:**
    `POST /uni/subscribe/username`
- **Pause/resume/delete by username:**
    `POST /uni/pause`, `/uni/resume`, `/uni/delete`
- **Query subscription info:**
    `GET /uni/info?username=...`

---

## 🔒 Security & Privacy

- No unnecessary data collection
- All sensitive actions require confirmation and/or secure API tokens
- Open codebase for full transparency
- Ready for security review

## 🛠️ Support & Customization

- **Contact:** Emil Popović (<admin@emilpopovic.me>)
- **GitHub:** [github.com/EmilPopovic/notifer](https://github.com/EmilPopovic/notifer)
- FER is welcome to audit, contribute, and adapt NotiFER for official use.

---

## 📄 License

MIT License – free for academic and non-commercial use.
