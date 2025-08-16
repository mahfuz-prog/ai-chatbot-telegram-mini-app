<script setup>
import { inject } from 'vue'

import Header from '../templates/Header.vue'
import MessageInput from './MessageInput.vue'

const store = inject("store")
</script>
<template>
  <Header />
  <div class="hero">
    <div class="title" />
    <hr>
    <div class="chat-messages">
      <div class="message-row model skeleton-row">
        <div class="avatar skeleton-avatar">🤖</div>
        <div class="message skeleton-bubble"></div>
      </div>
      <div class="message-row user skeleton-row">
        <div class="message skeleton-bubble"></div>
        <img :src="store.authState.profilePic" />
      </div>
      <div class="message-row model skeleton-row">
        <div class="avatar skeleton-avatar">🤖</div>
        <div class="message skeleton-bubble"></div>
      </div>
      <div class="message-row user skeleton-row">
        <div class="message skeleton-bubble"></div>
        <img :src="store.authState.profilePic" />
      </div>
    </div>
  </div>
  <MessageInput class="is-disabled" />
</template>

<style scoped>
@media (max-width: 768px) {
  .hero {
    width: 100%;
    height: calc(100% - 70px);
    padding: 20px;
  }
  .title {
    height: 23px;
    width: 250px;
    border-radius: 15px;
    animation: pulse-bg 1s infinite;
  }
  hr {
    height: 0;
    border: 0;
    border-top: 2px solid;
    margin-top: 5px;
    animation: pulse-border 1s infinite;
  }
  .chat-messages {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding-top: 20px;
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
  img {
    width: 34px;
    height: 34px;
    object-fit: cover;
    border: 2px solid var(--tertiary-black);
    border-radius: 50%;
  }
  .skeleton-avatar {
    background-color: var(--tertiary-black);
    color: white;
    font-weight: bold;
    width: 34px;
    height: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    border-radius: 50%;
  }
  .skeleton-bubble {
    height: 35px;
    width: 70%;
    border-radius: 14px;
    animation: pulse-bg 1s infinite;
  }
  .message-row.user .avatar {
    order: 2;
  }
  .message-row.user .skeleton-bubble {
    border-bottom-right-radius: 0;
  }
  .message-row.model .skeleton-bubble {
    border-bottom-left-radius: 0;
  }
  .is-disabled {
    pointer-events: none;
    cursor: not-allowed;
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
  @keyframes pulse-border {
    0% {
      border-color: rgb(12 187 197 / 15%);
    }
    50% {
      border-color: var(--tertiary-black);
    }
    100% {
      border-color: rgb(12 187 197 / 15%);
    }
  }
}
</style>
