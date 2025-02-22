# 📅 NotiFER

**NotiFER** is a web application designed for students at FER (Fakultet elektrotehnike i računarstva). NotiFER (a pun on "notifier" and FER, and "naughty FER" because they changed the timetable again) automatically monitors your university calendar and sends you an email notification whenever a change is detected (if you're a student at FER, that is). This way, you never miss an update to your class schedule or important events.

## ✅ Features

- **Automatic Calendar Change Detection:**  
    Once you sign up and confirm your subscription, NotiFER continuously monitors your FER calendar (provided in iCal format) for any changes. When a change is detected, you receive an email notification with the details.

## 🤔 How It Works

1. **Sign Up:**  
    Visit our website and paste your FER calendar URL.
2. **Confirm Subscription:**  
    A confirmation email is sent to your FER email address. Click the link in that email to activate your subscription.
3. **Receive Notifications:**  
    After activation, NotiFER monitors your calendar and sends you a notification email whenever any changes occur.

> **Note:**  
> NotiFER is intended to be used via the hosted service. Self-hosting is not recommended because the application depends on external services (such as Supabase for the database and Resend for emails) and features a complex deployment pipeline.

## 🛠️ Architecture

NotiFER is built with the following technologies:

- **FastAPI**: For the backend API.
- **Jinja2**: For templating, especially for rendering notification emails.
- **Docker & Docker Swarm/Compose**: For containerization and deployment.
- **External Services**: Utilizes services like Supabase for database management and Resend for email delivery.

## ⏭️ Deployment [![Phare badge](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus.notifer.emilpopovic.me%2Fshield-badges%2Fstatus.json&style=flat)](https://status.notifer.emilpopovic.me)

The project includes a sophisticated CI/CD pipeline that builds and deploys the containers to a production environment using Docker Swarm. This pipeline automates:

- Building Docker images.
- Pushing images to a container registry.
- Deploying the stack to a local server in Zagreb with proper service scaling and secret management.

## ⚖️ License

NotiFER is open source and available under the [MIT License](LICENSE).

## 📞 Contact

For any questions, issues, or support, please contact: admin@emilpopovic.me.

---

_NotiFER is developed and maintained by me, Emil, currently a student at FER._ 🦄
