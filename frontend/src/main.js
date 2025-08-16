import './assets/main.css'

import axios from 'axios'
import App from './App.vue'
import store from "./store"
import router from './router'
import { createApp } from 'vue'

// server address
axios.defaults.baseURL = store.authState.SERVER_ADDR
// axios.defaults.headers.common['X-Telegram-Init-Data'] = window.Telegram.WebApp.initData
axios.defaults.headers.common['X-Telegram-Init-Data'] = "query_id=AAEPsHoIAwAAAA-weghhrZhz&user=%7B%22id%22%3A6584709135%2C%22first_name%22%3A%22Mahfuz%22%2C%22last_name%22%3A%22Rahman%22%2C%22username%22%3A%22mahfuz5676%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FzF4ipl95HZ3J3ZK5TNHrl6dj87Ai1RWUwEI8ZUCKaqnw_G7kp67smDoKmx8xLvjn.svg%22%7D&auth_date=1755325669&signature=d-tB-7rgB-2hQWiihLDkYkK52uRXQbjzL5CIqel6WZBZMd_ISJoUY04ItkODYzd-MvxbQjW-6yvgGqjD-0_GBg&hash=e2b90c067a2db136301d428fbf088ec99334c8b679f2ec866a004b179abd07f7"

const app = createApp(App)

// make accessable reactive store object to the entire app
app.provide("store", store)
app.use(router)
app.mount('#app')