<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { ElNotification } from 'element-plus'
import apiClient from '@/api/client'
import type { Playlist } from '@/api/types/playlist'
import { AppRoutes } from '@/constants/appRoutes'

const router = useRouter()

const playlists = ref<Playlist[]>([])
const isLoading = ref(false)

async function fetchPlaylists() {
  try {
    isLoading.value = true
    const response = await apiClient.get<Playlist[]>('/playlists')
    playlists.value = response.data
  } catch (error) {
    ElNotification({
      message: 'Error loading playlists',
      type: 'error',
      duration: 3000,
    })
  } finally {
    isLoading.value = false
  }
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('ru-RU')
}

function onAddPlaylistClick() {
  ElNotification({
    message: 'Playlist creation will be added later',
    type: 'info',
    duration: 3000,
  })
}

onMounted(() => {
  fetchPlaylists()
})
</script>

<template>
  <div class="w-full h-full relative">
    <div class="mb-6">
      <h1 class="text-3xl font-bold dark:text-white">Playlists</h1>
    </div>

    <div v-if="isLoading" class="flex justify-center items-center flex-1">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>
    <div v-else-if="playlists.length === 0" class="flex flex-col justify-center items-center flex-1 text-gray-500 dark:text-gray-400">
      <p class="text-lg">No playlists</p>
      <p class="text-sm">Create your first playlist</p>
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="playlist in playlists"
        :key="playlist.id"
        class="p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all cursor-pointer"
      >
        <h3 class="font-semibold text-lg mb-2 dark:text-white">{{ playlist.title }}</h3>
        <p v-if="playlist.description" class="text-sm text-gray-600 dark:text-gray-300 mb-2">
          {{ playlist.description }}
        </p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">
          Tracks: {{ playlist.song_ids?.length || 0 }}
        </p>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          Created: {{ formatDate(playlist.created_at) }}
        </p>
      </div>
    </div>

    <button
      @click="onAddPlaylistClick"
      class="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-blue-500 hover:bg-blue-600 text-white shadow-lg flex items-center justify-center transition-all z-50 dark:bg-blue-600 dark:hover:bg-blue-700 cursor-pointer"
    >
      <span class="text-2xl font-bold">+</span>
    </button>
  </div>
</template>

<style scoped>
</style>

