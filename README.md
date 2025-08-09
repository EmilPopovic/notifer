# 📅 NotiFER

[![Status](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus.notifer.emilpopovic.me%2Fshield-badges%2Fstatus.json&style=flat)](https://status.notifer.emilpopovic.me)
[![License](https://img.shields.io/github/license/myolnyr/NotiFER)](https://github.com/myolnyr/NotiFER/blob/master/LICENSE)
[![Release](https://img.shields.io/github/v/release/myolnyr/NotiFER)](https://github.com/myolnyr/NotiFER/releases)

---

**NotiFER** is a modern, open-source web application designed for students at FER (Fakultet elektrotehnike i računarstva).
It automatically monitors university calendars and sends timely email notifications about timetable changes, ensuring students never miss and update.

---

## 🚀 Key Features

- **Automatic Calendar Change Detection:**
    Monitors FER iCal calendars and notifies students by email whenever a change is detected.

- **Easy Subscription:**
    Students simply paste their FER calendar URL to subscribe.

- **Secure & Privacy-Respecting:**
    No unecessary data is collected. All sensitive operations are protected and GDPR-friendly.

- **Internationalization:**
    Fully localized in Croatian and English.

- **University API:**
    FER administration can securely manage subscriptions (add, remove, pause, resume, query) via a protected API.

- **Self-Hosting Ready:**
    Easily deployable via Docker Compose, with built-in monitoring and metrics.

---

## 🎓 Why NotiFER?

- **Reliability:**
    Developed and maintained by a FER student, NotiFER has already detected hundreds of schedule changes and helped students stay up-to-date with their studies.

- **Open Source:**
    FER can freely review, audit, and contribute to the codebase.

- **University Integration:**
    NotiFER is ready for official FER deployment, with features for administrative control and secure management.

---

## 🤔 How It Works

1. **Sign Up:**
    Students visit the website and paste their FER calendar URL.
2. **Confirm Subscription:**
    A confirmation email is sent to their FER email address. They activate their subscription by clicking the link.
3. **Receive Notifications:**
    NotiFER monitors their calendar and sends an email notification whenever a change occurs.

---

## ☁️ Hosting & Deployment

NotiFER is production-ready and can be hosted by FER IT or any university department.

### Quick Start (Docker compose)

1. **Install Docker:**
    [Official instructions](https://docs.docker.com/engine/install/)

2. **Create the required Docker network:**

    ```bash
    docker network create proxy-network
    ```

3. **Clone the repository:**

    ```bash
    git clone https://github.com/myolnyr/NotiFER.git
    cd NotiFER
    ```

4. **Configure environment:**

    Edit `.env.example` and `config/app.conf` as needed, then rename:

    ```bash
    mv .env.example .env
    ```

5. **Run the service:**

    ```bash
    docker compose up --build -d
    ```

6. **Set up a reverse proxy (optional):**
    The app runs on port 8026. Metrics are available for Prometheus/Grafana integration.

---

## 🔒 Security & Privacy

- **No unecessary data collection.**
- **All sensitive actions require confirmation and/or secure API tokens.**
- **Open codebase for full transparency.**
- **Ready for university IT security review.**

---

## 🛠️ University API

FER administration can:

- Add or remove subscriptions via secure API endpoints.
- Pause or resume notifications for any user.
- Query subscription status and details.
- All actions require a secure API token (see documentation)

---

## ⚖️ License

NotiFER is open source and available under the [MIT License](LICENSE)

---

## 📞 Contact

For questions, support, or a demo, please contact:
**Emil Popović**
<admin@emilpopovic.me>

---

_NotiFER is currently developed and maintained by Emil Popović, a student at FER. Ready for official FER deployment and further collaboration!_ 🦄
