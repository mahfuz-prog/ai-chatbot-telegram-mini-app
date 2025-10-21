# Telegram mini app. Ai chatbot

## High-Level Architecture
<img width="896" height="2230" alt="telegram-mini-app" src="https://github.com/user-attachments/assets/4efbb23b-f8db-4ab6-a688-412712ad9b9c" />
<img width="909" height="1503" alt="mini-app-ui" src="https://github.com/user-attachments/assets/aeb883c6-b463-4fbb-b59e-2c3d8c8251a8" />

## Overview

This project is a Telegram Mini App that integrates a conversational AI-powered chatbot with a secure, scalable web application. The chatbot runs inside Telegram, with a Vue.js frontend injected into the Telegram webview and a Django REST backend handling authentication, authorization, conversation management, and AI integration.

**The system demonstrates advanced full-stack engineering by combining:**
* Real-time chat within Telegram
* Secure Telegram query validation - HMAC
* A Gemini AI model for natural language responses and function calling
* Weather API integration for external data fetching

This application highlights system design, API development, AI integration, and cloud deployment skills.

## Flow Overview

#### Telegram App Integration
* The chatbot is launched as a Telegram Mini App.
* Telegram injects the window.Telegram object into the frontend, providing a telegram authorized user details.
* A private bot token validates user authenticity by generating and verifying secure query strings with Telegram servers.

#### Frontend (Vue.js)
* A responsive Vue.js SPA runs inside Telegram’s webview.
* Handles user interaction, chat interface, and sends API requests to the backend.

#### Backend (Django REST + Gunicorn + Nginx)
* Nginx serves as reverse proxy and SSL terminator.
* Gunicorn runs the Django server handling API requests.
* Django validates Telegram query strings, ensuring only authenticated users can access the system.
* The chatbot engine processes messages, integrates with the Gemini AI model, and triggers function calls.

#### AI Model Integration (Gemini)
* The AI chatbot uses Gemini 2.5 for generating intelligent responses.
* Fetching weather data from an external Weather API.
* Returning contextual responses based on stored chat history.

#### Database - SQLite
* Users: Telegram IDs, usernames, join timestamps.
* Chats: Chat sessions with unique identifiers.
* Messages: Full conversation history.
* Chat Contexts: Context data for preserving conversational memory.

#### Security & Scalability
* VM Firewall restricts access to backend services.
* CORS ensures secure frontend-backend communication.

 
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
GENAI_API=""
BOT_TOKEN=""
VALID_AUTH_DATE_WINDOW_SECONDS=360000000000000000000000
WEATHER_API=""
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