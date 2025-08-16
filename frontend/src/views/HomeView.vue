<script setup>
import { ref, inject, onErrorCaptured } from 'vue'
import { viewErrorHandler } from '@/utils/errorHandler'

import Header from '../components/templates/Header.vue'
import Footer from '../components/templates/Footer.vue'
import Error from "../components/templates/Error.vue"
import Content from '../components/homepage/Content.vue'
import ContentSkeleton from '../components/homepage/ContentSkeleton.vue'

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
  <Header />
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
    <Error :err="error" :showBtn="false" v-if="error" />
  </div>
  <Footer />
</template>

<style scoped>
.page {
  height: calc(100vh - 112px);
  background-color: var(--primary-black);
}
</style>
