<script setup>
import { ref, inject, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useNotify } from '../composables/useNotify'

import axios from 'axios'
import Header from '../templates/Header.vue'
import MessageInput from './MessageInput.vue'
import Conversations from './Conversations.vue'

const store = inject("store")
const route = useRoute()
const notify = useNotify()

const uniqueHexId = ref(route.params.uniqueHexId || "")

try {
  if (uniqueHexId.value) {
    const { data } = await axios.get(`/chat/single-chat/${uniqueHexId.value}`)
    nextTick(() => {
      store.activeChatActions.setActiveChat(data.single_chat)
    })
  } else {
    notify.show('Error', 'Failed to load chat', 'error')
  }
} catch (err) {
  throw err
}
</script>
<template>
  <Header />
  <div class="hero">
    <Conversations />
  </div>
  <MessageInput />
</template>

<style scoped>
@media (max-width: 768px) {
  .hero {
    width: 100%;
    height: calc(100% - 70px);
    padding: 20px;
    overflow: scroll;
  }
  h3 {
    color: #ffffff;
  }
}
</style>
