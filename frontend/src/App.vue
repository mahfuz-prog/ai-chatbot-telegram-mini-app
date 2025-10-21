<script setup>
import { ref, inject, onMounted, onUnmounted } from 'vue'
import { RouterView, useRouter } from 'vue-router'

import axios from 'axios'
import ContentSkeleton from './components/homepage/ContentSkeleton.vue'

const store = inject("store")
const router = useRouter()

const loading = ref(false)
const error = ref(false)

// telegram webapp information
const telegramClient = window.Telegram.WebApp

// set header color of telegram app
telegramClient.headerColor = '#0CBBC5'

// telegram back button functionality
telegramClient.BackButton.onClick(() => {
  router.go(-1)
})

// parse the telegram initData to get user info
onMounted(async() => {
  try {
    loading.value = true
    const { data } = await axios.get('/users/')
    const initData = new URLSearchParams(telegramClient.initData)
    const user = JSON.parse(initData.get("user"))
    store.authActions.setAuthInfo(user)
  } catch (err) {
    // if error occured close the telegram app
    if (err.response && (err.response.status === 401 || err.response.status === 403)) {
      telegramClient.close()
    }
  } finally {
    loading.value = false
  }
})

// reset all the states
onUnmounted(() => {
  store.authActions.resetAuth()
  store.chatActions.resetChats()
  store.activeChatActions.resetActiveChat()
})
</script>
<template>
  <main>
    <template v-if="!error">
      <RouterView v-if="!loading" />
    </template>
    <div class="error" v-else>
      <i><h1>Only accessable from telegram mini app</h1></i>
    </div>
    <ContentSkeleton v-if="loading" />
  </main>
</template>

<style>
html,
body,
#app {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
}

main {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.error {
  flex: 1;
  display: grid;
  place-content: center;
}

h1 {
  font-weight: 700;
  text-align: center;
  color: #dc3545;
  line-height: 35px;
}
</style>
