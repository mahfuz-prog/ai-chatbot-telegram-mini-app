<script setup>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useNotify } from '../composables/useNotify'

import axios from 'axios'
import DeleteIcon from '../icons/DeleteIcon.vue'

const store = inject("store")
const router = useRouter()
const notify = useNotify()

const isLoading = ref(false)

// get the all chat from current user
try {
  const { data } = await axios.get('/chat/chat-list/')
  store.chatActions.setChats(data.chat_list)
} catch (err) {
  throw err
}

// redirect to the chat page with chat it
const goToChat = (unique_hex_id) => {
  router.push({ name: "chat", params: { uniqueHexId: unique_hex_id } })
}

// create new chat
const newChat = async() => {
  isLoading.value = true
  try {
    const { data } = await axios.post('/chat/new-chat/')
    store.chatActions.addChatAtBeginning(data.new_chat)
    notify.show('Success', 'A new chat created', 'success')
  } catch (err) {
    notify.show('Error', 'Failed to create a new chat', 'error')
  } finally {
    isLoading.value = false
  }
}

// delete chat
const deleteChat = async(chatId) => {
  isLoading.value = true
  try {
    await axios.delete(`/chat/delete-chat/${chatId}/`)
    store.chatActions.deleteChat(chatId)
    notify.show('Success', 'Successfully chat deleted', 'success')
  } catch (err) {
    notify.show('Error', 'Failed to delete chat', 'error')
  } finally {
    isLoading.value = false
  }
}
</script>
<template>
  <div class="hero">
    <div class="chat-history" v-if="store.chatState.chatList.size > 0">
      <div class="chats">
        <div v-for="[idx, chat] in store.chatState.chatList" :key="idx" class="chat-item">
          <button @click="goToChat(chat.unique_hex_id)" class="select-button" :disabled="isLoading"> {{ chat.title }}... </button>
          <button @click="deleteChat(idx)" :disabled="isLoading" class="delete-button">
            <DeleteIcon :width="16" :height="18" :iconFillColor="isLoading ? '#a0a0a0' : '#dc3545'" />
          </button>
        </div>
      </div>
      <div class="new-chat">
        <button @click="newChat" :disabled="isLoading" :class="{'deactive' : isLoading}">New Chat</button>
      </div>
    </div>
    <div class="empty-chat" v-else>
      <h1>Hello {{ store.authState.firstName }}</h1>
      <p>This is a AI assistant powered by Gemini, designed to answer questions, fetch live weather updates, and chat naturally. Ask anything — like "What’s the weather like in Dhaka?</p>
      <button @click="newChat" :disabled="isLoading" :class="{'deactive' : isLoading}">Start Chatting</button>
    </div>
  </div>
</template>

<style scoped>
@media (max-width: 768px) {
  .hero {
    width: 100%;
    height: 100%;
    padding: 20px;
  }
  .chat-history {
    width: 100%;
    height: 100%;
    padding: 20px;
    border: 1px solid var(--tertiary-black);
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 10px;
    background-color: var(--secondary-black);
  }
  .chats {
    display: flex;
    flex-direction: column;
    gap: 10px;
    overflow-y: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }
  .chats::-webkit-scrollbar {
    display: none;
  }
  .chat-item {
    border: 1px solid var(--accent);
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: var(--primary-black);
  }
  .select-button {
    width: 100%;
    background-color: transparent;
    text-align: left;
    padding-left: 15px;
    padding-right: 15px;
  }
  .delete-button {
    padding-left: 15px;
    padding-right: 15px;
    background-color: transparent;
  }
  span {
    color: #ffffff;
  }
  .new-chat button {
    width: 100% !important;
  }
  .empty-chat {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 15px;
  }
  h1 {
    width: 330px;
    text-align: center;
    font-size: 30px;
    font-weight: 700;
    line-height: 32px;
    color: #ffffff;
  }
  p {
    text-align: center;
    color: #ebebeba3;
  }
  button {
    padding: 10px 30px;
    background-color: var(--tertiary-black);
    border: 0;
    border-radius: 3px;
    color: #ffffff;
  }
  .deactive {
    animation: pulse-bg 1s infinite;
  }
  @keyframes pulse-bg {
    0% {
      background-color: rgb(12 187 197 / 15%);
    }
    50% {
      background-color: var(--tertiary-black);
    }
    100% {
      background-color: rgb(12 187 197 / 15%);
    }
  }
}
</style>
