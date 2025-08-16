<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  err: {
    type: String,
    required: false,
    default: "An unexpected error occurred.",
  },
  showBtn: {
    type: Boolean,
    default: true,
  }
})

const router = useRouter()
</script>
<template>
  <div class="section">
    <i><h1>{{ props.err }}</h1></i>
    <button v-if="props.showBtn" @click="router.push({name: 'home'})">Return Home</button>
  </div>
</template>

<style scoped>
@media (max-width: 768px) {
  .section {
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    place-items: center;
    justify-content: center;
    gap: 20px;
  }
  h1 {
    font-weight: 700;
    text-align: center;
    color: #ebebeba3;
    line-height: 35px;
  }
  button {
    border: 0;
    padding: 10px 30px;
    border-radius: 25px;
    background-color: var(--accent);
    color: #ffffff;
  }
}
</style>
