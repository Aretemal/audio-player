<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { ElNotification } from 'element-plus'
import apiClient from '@/api/client'
import { bookmarkService } from '@/api/services/bookmarkService'
import type { Album } from '@/api/types/album'
import type { Bookmark } from '@/api/types/bookmark'

const router = useRouter()

const albums = ref<Album[]>([])
const bookmarks = ref<Bookmark[]>([])
const isLoading = ref(false)

const savedReleases = computed(() =>
  bookmarks.value.filter((b) => b.bookmark_type === 'album')
)

async function fetchAlbums() {
  try {
    isLoading.value = true
    const [albumsRes, bookmarksRes] = await Promise.all([
      apiClient.get<Album[]>('/albums'),
      bookmarkService.getAll({ bookmark_type: 'album' }),
    ])
    albums.value = albumsRes.data
    bookmarks.value = bookmarksRes.data
  } catch (error) {
    ElNotification({
      message: 'Error loading data',
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

function openRelease(mbid: string) {
  router.push(`/releases/${mbid}`)
}

onMounted(() => {
  fetchAlbums()
})
</script>

<template>
  <div class="w-full h-full flex flex-col gap-6">
    <h1 class="text-2xl font-bold dark:text-white">My Albums</h1>
    <p class="text-gray-600 dark:text-gray-400">
      Albums from your collection and saved releases from search.
    </p>

    <div v-if="isLoading" class="flex justify-center items-center py-12">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>

    <template v-else>
      <section v-if="albums.length > 0">
        <h2 class="text-lg font-semibold dark:text-white mb-3">Collection</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="album in albums"
            :key="album.id"
            class="p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all"
          >
            <h3 class="font-semibold text-lg mb-2 dark:text-white">{{ album.title || 'Untitled' }}</h3>
            <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">Artist: {{ album.creator || 'Unknown' }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">Tracks: {{ album.song_ids?.length || 0 }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">Created: {{ formatDate(album.created_at) }}</p>
          </div>
        </div>
      </section>

      <section v-if="savedReleases.length > 0">
        <h2 class="text-lg font-semibold dark:text-white mb-3">Saved Releases</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="b in savedReleases"
            :key="b.id"
            class="p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all cursor-pointer"
            @click="openRelease(b.musicbrainz_id)"
          >
            <h3 class="font-semibold text-lg dark:text-white truncate">{{ b.title }}</h3>
          </div>
        </div>
      </section>

      <div
        v-if="albums.length === 0 && savedReleases.length === 0"
        class="flex flex-col justify-center items-center py-20 text-gray-500 dark:text-gray-400"
      >
        <p class="text-lg">No albums</p>
        <p class="text-sm">Add songs to your collection or save releases from Search</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
</style>
