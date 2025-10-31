# Telegram AI Chatbot Mini App

## High-Level Architecture
<img width="896" height="2230" alt="telegram-mini-app" src="https://github.com/user-attachments/assets/4efbb23b-f8db-4ab6-a688-412712ad9b9c" />
<img width="909" height="1503" alt="mini-app-ui" src="https://github.com/user-attachments/assets/aeb883c6-b463-4fbb-b59e-2c3d8c8251a8" />

## Overview

This project is a Telegram Mini App integrating an **Agentic AI (GraphBit)** powered chatbot with a secure, scalable web application. The chatbot runs inside Telegram, with a Vue.js frontend injected into the Telegram webview and a Django REST backend managing authentication, authorization, conversation flow, and AI processing.

## Key highlights of this project include:
* **Agentic AI framework (Graphbit)** for autonomous reasoning and task execution
* Real-time chat within Telegram Mini App
* Secure Telegram query validation via HMAC
* Weather API integration for dynamic responses
* Full-stack development using Vue.js frontend and Django REST backend
* Production-ready deployment with Docker and PostgreSQL
* Robust logging and comprehensive automated tests
* This application highlights system design, API development, AI integration, and cloud deployment skills.


## System Architecture
### Telegram Mini App Integration
* The chatbot is launched inside Telegram as a Mini App.
* Telegram injects the window.Telegram object into the frontend, providing authorized user details.
* A secure bot token validates the user via HMAC-verified query strings.

### Frontend (Vue.js)
* Responsive single-page application (SPA) running inside Telegram webview.
* Handles user interactions and sends API requests to the backend.
* Uses CORS and secure headers to communicate safely with the Django backend.* A responsive Vue.js SPA runs inside Telegram’s webview.

#### Backend (Django REST + Gunicorn + Nginx)
* Nginx serves as reverse proxy and SSL terminator.
* Gunicorn runs the Django server to handle REST API requests.
* Django validates Telegram query strings and ensures only authorized users can access services.
* Agentic AI framework (Graphbit) processes messages and handles automated tasks.
* Logging is integrated throughout the application to track errors, warnings, and debug information.

#### AI Agent (Graphbit)
* Replaces previously used Gemini AI for autonomous reasoning and task execution.
* Maintains conversational context and can call external functions (e.g., Weather API).
* Generates intelligent, contextual responses to user messages.

#### Database - SQLite
* PostgreSQL for production-grade, reliable storage.
* SQLite may be used in development for simplicity
**Schema**
`Users`: Telegram IDs, usernames, join timestamps
`Chats`: Chat sessions with unique identifiers
`Messages`: Full conversation history
`ChatContext`: Persistent context for conversation memory

#### Security & Scalability
* HMAC validation ensures only authentic Telegram users can interact.
* CORS configuration protects frontend-backend communication.
* PostgreSQL enables production-grade reliability and scaling.
* Docker containers provide reproducible and isolated environments.
* Logging system captures errors, warnings, and debug info across services.

#### Testing
* Unit tests cover models, serializers, services, and decorators.
* Integration tests validate full chat flow including AI responses.
* Run tests: `python manage.py test`


# Third party service integration
## Create account and get an free api key
* (OpenRouter -> Interface for LLMs)[https://openrouter.ai/settings/keys]
* (weatherapi -> Realtime weather update)[https://www.weatherapi.com/docs/]
* (Telegram bot config)[https://core.telegram.org/bots/webapps]
* (Bot Token: BotFather -> /newbot -> Token)[https://web.telegram.org/a/]

 
# Development
=================================================

## Backend
### Export base `.env`
```bash
SECRET_KEY=hola
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,example.com
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://example.com
CORS_PREFLIGHT_MAX_AGE=1800
BOT_TOKEN=""
WEATHER_API=""
OPENROUTER_API_KEY=""
VALID_AUTH_DATE_WINDOW_SECONDS=360000000000000000000000
DB_HOST=postgresdb
POSTGRES_DB=app
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```

### Create image & run container application layer
```bash
docker build -t django-backend:dev .
docker run --name django-app --env-file .env -p8000:8000 django-backend:dev
```

### Database Migration if running without docker
```bash
python manage.py makemigrations users
python manage.py makemigrations chats
python manage.py migrate
```


## Frontend
### Export base `.env`
```bash
VITE_SERVER_ADDR=http://localhost:8000/api-v2
VITE_USE_FAKE_USER=true
VITE_USER_NAME=mahfuz5676
VITE_FIRST_NAME=Mahfuz
VITE_LAST_NAME=Rahman
VITE_PROFILE_PIC=https://t.me/i/userpic/320/zF4ipl95HZ3J3ZK5TNHrl6dj87Ai1RWUwEI8ZUCKaqnw_G7kp67smDoKmx8xLvjn.svg
VITE_FAKE_INIT_DATA=query_id=AAEPsHoIAwAAAA-weghhrZhz&user=%7B%22id%22%3A6584709135%2C%22first_name%22%3A%22Mahfuz%22%2C%22last_name%22%3A%22Rahman%22%2C%22username%22%3A%22mahfuz5676%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FzF4ipl95HZ3J3ZK5TNHrl6dj87Ai1RWUwEI8ZUCKaqnw_G7kp67smDoKmx8xLvjn.svg%22%7D&auth_date=1755325669&signature=d-tB-7rgB-2hQWiihLDkYkK52uRXQbjzL5CIqel6WZBZMd_ISJoUY04ItkODYzd-MvxbQjW-6yvgGqjD-0_GBg&hash=e2b90c067a2db136301d428fbf088ec99334c8b679f2ec866a004b179abd07f7
```

### Create image & run container application layer
```bash
docker build -f Dockerfile-dev -t vue-frontend:dev .
docker run --name vue-app --env-file .env -p5173:5173 vue-frontend:dev
```

## Run development environment, docker compose
```bash
docker compose -f dev-docker-compose.yml up
docker compose -f dev-docker-compose.yml down
```


# Production Service-based architecture
=================================================

**Run entire application using docker compose.**
- .env for backend and frontend
- update nginx.conf in frontend according to backend url
- build the vue app locally
- In one container nginx + vue build(/dist)

## Backend
### Override `.env` variable from `docker-compose.yml`
```sh
environment:
  - DEBUG=False
  - CORS_ALLOWED_ORIGINS=http://localhost:8080
```

## Frontend
### export `.env.production` for override `.env` in build process
```sh
VITE_SERVER_ADDR=http://localhost:8000/api-v2
VITE_USE_FAKE_USER=false
```

### build vue app locally
```sh
npm install
npm run build -- --mode production
```

## Run entire app in production
```bash
docker compose up -d
docker compose down
```