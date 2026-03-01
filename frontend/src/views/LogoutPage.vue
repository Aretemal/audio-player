<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { AppRoutes } from '@/constants/appRoutes'
import { Loading } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  await authStore.logout()
  router.push(AppRoutes.LOGIN)
})
</script>

<template>
  <div class="flex justify-center items-center min-h-screen">
    <div class="text-center">
      <el-icon class="is-loading mb-4" :size="40"><Loading /></el-icon>
      <p class="text-gray-600 dark:text-gray-400">Logging out...</p>
    </div>
  </div>
</template>

<style scoped>
</style>
