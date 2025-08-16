<script setup>
import { ref, inject, onErrorCaptured } from 'vue'
import { viewErrorHandler } from '@/utils/errorHandler'

import Error from "../components/templates/Error.vue"
import Content from '../components/chatpage/Content.vue'
import ContentSkeleton from '../components/chatpage/ContentSkeleton.vue'

const store = inject("store")

const error = ref("")

const viewErrorHandlerCallback = viewErrorHandler({
  store,
  errorRef: error
})

// handle the error
onErrorCaptured(viewErrorHandlerCallback)
</script>
<template>
  <div class="page">
    <template v-if="!error">
      <Suspense>
        <template #default>
          <Content/>
        </template>
        <template #fallback>
          <ContentSkeleton />
        </template>
      </Suspense>
    </template>
    <Error :err="error" v-if="error" />
  </div>
</template>

<style scoped>
.page {
  height: 100vh;
  background-color: var(--primary-black);
}
</style>
