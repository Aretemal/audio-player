<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useSongStore } from '@/stores/song'
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { AppRoutes } from '@/constants/appRoutes'

const songStore = useSongStore()
const router = useRouter()

const songs = computed(() => songStore.songs)
const isLoading = computed(() => songStore.isLoading)

function onAddSongClick() {
  router.push(AppRoutes.CREATE_SONG)
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

onMounted(() => {
  songStore.fetchSongs()
})
</script>

<template>
  <div class="w-full h-full relative">
    <div class="flex flex-col gap-2 h-full overflow-y-auto">
      <div v-if="isLoading" class="flex justify-center items-center flex-1">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      </div>
      <div v-else-if="songs.length === 0" class="flex flex-col justify-center items-center flex-1 text-gray-500 dark:text-gray-400">
        <p class="text-lg">No songs</p>
        <p class="text-sm">Add your first song to get started</p>
      </div>
      <div
        v-else
        v-for="song in songs"
        :key="song.id"
        class="p-4 rounded-lg transition-all hover:bg-gray-100 dark:hover:bg-gray-700 border-b border-gray-200 dark:border-gray-700"
      >
        <div class="flex flex-col gap-3">
          <div class="flex flex-col gap-1 flex-1 min-w-0">
            <h3 class="font-semibold text-lg truncate dark:text-white">{{ song.title || 'Untitled' }}</h3>
            <p class="text-sm text-gray-600 dark:text-gray-300 truncate">{{ song.artist || 'Unknown artist' }}</p>
            <p v-if="song.album" class="text-xs text-gray-500 dark:text-gray-400 truncate">Album: {{ song.album }}</p>
          </div>
          <div class="flex gap-2 items-center">
            <audio
              :src="songStore.getStreamUrl(song.id)"
              controls
              class="flex-1"
            />
          </div>
          <div class="flex justify-between items-center text-xs text-gray-500 dark:text-gray-400">
            <span>Added: {{ new Date(song.created_at).toLocaleDateString() }}</span>
            <span v-if="song.file_size">
              Size: {{ formatFileSize(song.file_size) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <button
      @click="onAddSongClick"
      class="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-blue-500 hover:bg-blue-600 text-white shadow-lg flex items-center justify-center transition-all z-50 dark:bg-blue-600 dark:hover:bg-blue-700"
    >
      <span class="text-2xl font-bold">+</span>
    </button>
  </div>
</template>

<style scoped>
</style>

