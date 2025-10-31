<script setup>
import { inject } from 'vue'
import { useRouter } from "vue-router"

const store = inject("store")
const router = useRouter()
</script>
<template>
  <header>
    <img :src="store.authState.profilePic" @click="router.push({name: 'home'})">
    <span @click="router.push({name: 'home'})">{{ store.authState.userName }}</span>
  </header>
</template>

<style scoped>
@media (max-width: 768px) {
  header {
    height: 70px;
    padding: 10px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: var(--secondary-black);
  }
  img {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    border: 2px solid var(--accent);
  }
  span {
    color: #ffffff;
  }
}
</style>
