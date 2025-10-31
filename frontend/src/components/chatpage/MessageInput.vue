<script setup>
import { ref, inject, nextTick, useTemplateRef } from 'vue'
import { useNotify } from '../composables/useNotify'

import axios from 'axios'
import SubmitIcon from '../icons/SubmitIcon.vue'
import SubmittingIcon from '../icons/SubmittingIcon.vue'

const store = inject("store")
const textareaRef = useTemplateRef("textareaRef")
const notify = useNotify()

const MIN_CONTENT_LENGTH = ref(3)
const MAX_CONTENT_LENGTH = ref(250)

const messageInput = ref("")
const isSubmitting = ref(false)
const error = ref(false)
const tempIdCounter = ref(-1)

const sendMessage = async() => {
  // already a pending request
  if (isSubmitting.value) return

  // validation
  if (
    messageInput.value.length < MIN_CONTENT_LENGTH.value ||
    messageInput.value.length > MAX_CONTENT_LENGTH.value
  ) return

  // remove previous error status
  error.value = false
  textareaRef.value.style.height = 'auto'

  const tempMessage = messageInput.value
  messageInput.value = ""

  // assign tempIdCounter in temp variable
  // and decrease 1 for next assignment
  const tempId = tempIdCounter.value
  tempIdCounter.value -= 1

  // temp user message obj
  const tempUserMessage = {
    id: tempId,
    sender: 'user',
    content: tempMessage,
    timestamp: new Date().toISOString(),
  }

  // temp bot reply
  const tempBotReply = {
    id: tempId - 1,
    sender: 'model',
    content: 'Loading...',
    timestamp: new Date().toISOString(),
    isLoading: true
  }

  // add those temp obj to state
  store.activeChatActions.addMessage(tempUserMessage)
  store.activeChatActions.addMessage(tempBotReply)

  try {
    isSubmitting.value = true
    const { data } = await axios.post("/chat/chatting/", {
      chat_id: store.activeChatState.id,
      content: tempMessage
    })

    // remove temp message objects
    store.activeChatActions.removeMessageById(tempId)
    store.activeChatActions.removeMessageById(tempId - 1)

    // update the state before proceeding
    nextTick(() => {
      store.activeChatActions.addMessage(data.user)
      store.activeChatActions.addMessage(data.model)

      // if there is a title in response
      if (data.title) {
        store.activeChatActions.setActiveChatTitle(data.title)
      }
    })
  } catch (err) {
    store.activeChatActions.removeMessageById(tempId)
    store.activeChatActions.removeMessageById(tempId - 1)
    messageInput.value = tempMessage
    error.value = true
    notify.show('Error', 'Failed to send message', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// calculate input box height
const autoResize = () => {
  const el = textareaRef.value
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 300) + 'px'
  }
}
</script>
<template>
  <div class="input-wrapper">
    <div class="input-box" :class="{ error: error }">
      <textarea v-model.trim="messageInput" placeholder="Type a message..." ref="textareaRef" @input="autoResize" @keyup.enter.exact.prevent="sendMessage" />
      <button class="submit" :disabled="!messageInput.trim()" @click="sendMessage">
        <SubmitIcon width="20" height="20" v-if="!isSubmitting" />
        <SubmittingIcon width="16" height="16" v-else />
      </button>
    </div>
  </div>
</template>

<style scoped>
@media (max-width: 768px) {
  .input-wrapper {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    padding: 10px 16px;
    background: var(--primary-black);
    z-index: 100;
  }
  .input-box {
    display: flex;
    align-items: center;
    background: var(--secondary-black);
    border-radius: 28px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    padding: 10px 14px;
    gap: 10px;
    transition: border 0.2s;
  }
  .input-box.error {
    border: 1px solid #ff4d4d;
  }
  textarea {
    color: #ffffff;
    flex: 1;
    border: none;
    resize: none;
    overflow-y: auto;
    padding: 6px 0;
    font-size: 15px;
    line-height: 20px;
    border-radius: 0;
    background: transparent;
    outline: none;
    max-height: 150px;
    min-height: 20px;
    font-family: inherit;
  }
  .submit {
    background: transparent;
    border: none;
    padding: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #1a73e8;
    transition: opacity 0.2s;
    cursor: pointer;
  }
  .submit:disabled {
    color: #ccc;
    cursor: default;
  }
  .input-box {
    padding: 12px 16px;
  }
}
</style>
