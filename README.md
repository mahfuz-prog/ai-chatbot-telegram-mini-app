# Backend Config

#### create a .env file inside BASE_DIR

```bash
SECRET_KEY=""
GENAI_API=""
BOT_TOKEN=""
WEATHER_API=""
VALID_AUTH_DATE_WINDOW_SECONDS=""
```

# Frontend

#### Hardcoded values

```bash
store.js -> authState
main.js -> axios.defaults.headers.common['X-Telegram-Init-Data']
vite.config.js -> server block
```

#### Ngrok
```bash
ngrok http --url=longhorn-smooth-lemur.ngrok-free.app 5173
```