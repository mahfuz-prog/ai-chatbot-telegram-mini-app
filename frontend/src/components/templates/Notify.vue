<script setup>
import { ref } from 'vue'

const visible = ref(false)
const title = ref('')
const message = ref('')
const type = ref('')

let timeout = null

const showNotify = (t, m, variant = 'info') => {
  title.value = t
  message.value = m
  type.value = variant
  visible.value = true

  clearTimeout(timeout)
  timeout = setTimeout(() => {
    visible.value = false
  }, 2000)
}

const dismiss = () => {
  visible.value = false
  clearTimeout(timeout)
}

defineExpose({ showNotify })
</script>
<template>
  <transition name="fade">
    <div v-if="visible" class="notify" :class="type" @click="dismiss">
      <strong>{{ title }}</strong>
      <p>{{ message }}</p>
    </div>
  </transition>
</template>

<style scoped>
.notify {
  position: fixed;
  top: 80px;
  right: 20px;
  background: #333;
  color: #fff;
  padding: 12px 20px;
  border-radius: 8px;
  z-index: 9999;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  min-width: 220px;
  max-width: 80vw;
  height: auto;
}

.notify.success {
  background: var(--accent);
}

.notify.error {
  background: #dc3545;
}

.notify.info {
  background: #0d6efd;
}

.notify p {
  margin: 4px 0 0 0;
  font-size: 13px;
  opacity: 0.9;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
