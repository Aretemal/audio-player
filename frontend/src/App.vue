<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppHeader from './widgets/AppHeader.vue';
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
    <AppHeader />
    <main class="flex-1 w-full px-10 py-4">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
#app {
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
}
</style>
