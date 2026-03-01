<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { bookmarkService } from '@/api/services/bookmarkService'
import type { Bookmark } from '@/api/types/bookmark'

const router = useRouter()
const bookmarks = ref<Bookmark[]>([])
const isLoading = ref(false)

const savedArtists = computed(() =>
  bookmarks.value.filter((b) => b.bookmark_type === 'artist')
)

async function fetchSaved() {
  try {
    isLoading.value = true
    const res = await bookmarkService.getAll({ bookmark_type: 'artist' })
    bookmarks.value = res.data
  } catch (e) {
    console.error(e)
    bookmarks.value = []
  } finally {
    isLoading.value = false
  }
}

function openArtist(mbid: string) {
  router.push(`/artists/${mbid}`)
}

onMounted(() => {
  fetchSaved()
})
</script>

<template>
  <div class="w-full h-full flex flex-col gap-4">
    <h1 class="text-2xl font-bold dark:text-white">My Artists</h1>
    <p class="text-gray-600 dark:text-gray-400">
      Only saved artists are shown here. Add them from the Search page.
    </p>

    <div v-if="isLoading" class="flex justify-center items-center py-20">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>
    <div
      v-else-if="savedArtists.length === 0"
      class="flex flex-col justify-center items-center py-20 text-gray-500 dark:text-gray-400"
    >
      <p class="text-lg">No saved artists</p>
      <p class="text-sm">Go to Search, find an artist and click Save</p>
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div
        v-for="b in savedArtists"
        :key="b.id"
        class="p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:shadow-md transition-shadow cursor-pointer"
        @click="openArtist(b.musicbrainz_id)"
      >
        <h3 class="font-semibold text-lg dark:text-white truncate" :title="b.title">
          {{ b.title }}
        </h3>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
