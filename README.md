# Telegram mini app. Ai chatbot

## High-Level Architecture
<img width="896" height="2230" alt="telegram-mini-app" src="https://github.com/user-attachments/assets/def5d855-3fc3-4aec-a5e8-8ab55c2aa194" />

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
