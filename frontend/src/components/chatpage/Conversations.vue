<script setup>
import { inject, onMounted, watch, nextTick } from 'vue'

const store = inject('store')

const scrollToBottom = () => {
  document.getElementById('bottom').scrollIntoView({ behavior: 'smooth' })
}

// Initial scroll
onMounted(() => {
  nextTick(() => {
    scrollToBottom()
  })
})

// Scroll on message change
watch(
  () => store.activeChatState.messages.size,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  }
)
</script>
<template>
  <!-- <div> -->
  <h3>{{ store.activeChatState.title }}</h3>
  <hr />
  <!-- </div> -->
  <div class="chat-messages">
    <template v-if="store.activeChatState.messages.size > 0">
      <div v-for="[idx, msg] in Array.from(store.activeChatState.messages)" :key="idx" :class="['message-row', msg.sender === 'user' ? 'user' : 'model']">
        <!-- Avatar -->
        <div class="avatar">
          <img v-if="msg.sender === 'user'" :src="store.authState.profilePic" alt="User Avatar" />
          <div v-else class="model-avatar">🤖</div>
        </div>
        <!-- Message bubble -->
        <div class="message" :class="{'loading-message' : msg.isLoading}">
          {{ msg.content }}
        </div>
      </div>
    </template>
    <template v-else>
      <div class="message-row model">
        <div class="avatar">
          <div class="model-avatar">🤖</div>
        </div>
        <div class="message">Hello {{ store.authState.userName }}. How can I assist you?</div>
      </div>
    </template>
    <div id="bottom"></div>
  </div>
</template>

<style scoped>
@media (max-width: 768px) {
  .chat-messages {
    display: flex;
    flex-direction: column;
    gap: 12px;
    overflow-y: auto;
    flex: 1;
    font-size: 15px;
    padding: 20px 0 70px;
    scroll-behavior: smooth;
    overflow: hidden;
  }
  .message-row {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    max-width: 100%;
  }
  .message-row.user {
    justify-content: flex-end;
  }
  .message-row.user .message {
    background-color: var(--accent);
    color: white;
    border-bottom-right-radius: 0;
  }
  .message-row.user .avatar {
    order: 2;
  }
  .message-row.model {
    justify-content: flex-start;
  }
  .message-row.model .message {
    background-color: var(--secondary-black);
    color: white;
    border-bottom-left-radius: 0;
  }
  .message {
    padding: 6px 14px;
    border-radius: 14px;
    max-width: 80%;
    word-break: break-word;
  }
  .avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border: 2px solid var(--tertiary-black);
    border-radius: 50%;
  }
  .model-avatar {
    background-color: var(--tertiary-black);
    color: white;
    font-weight: bold;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    border-radius: 50%;
  }
  .loading-message {
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
