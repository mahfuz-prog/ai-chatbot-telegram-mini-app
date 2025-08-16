import './assets/main.css'

import axios from 'axios'
import App from './App.vue'
import store from "./store"
import router from './router'
import { createApp } from 'vue'

// server address
axios.defaults.baseURL = store.authState.SERVER_ADDR
axios.defaults.headers.common['X-Telegram-Init-Data'] = window.Telegram.WebApp.initData

const app = createApp(App)

// make accessable reactive store object to the entire app
app.provide("store", store)
app.use(router)
app.mount('#app')