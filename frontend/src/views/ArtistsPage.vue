<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { bookmarkService } from '@/api/services/bookmarkService'
import type { Bookmark } from '@/api/types/bookmark'
import AlbumCard from '@/components/AlbumCard.vue'

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
    <h1 class="text-2xl font-bold text-stone-100">My Artists</h1>
    <p class="text-stone-400">
      Only saved artists are shown here. Add them from the Search page.
    </p>

    <div v-if="isLoading" class="flex justify-center items-center py-20">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>
    <div
      v-else-if="savedArtists.length === 0"
      class="flex flex-col justify-center items-center py-20 text-stone-500"
    >
      <p class="text-lg">No saved artists</p>
      <p class="text-sm">Go to Search, find an artist and click Save</p>
    </div>
    <div v-else class="flex flex-wrap gap-4">
      <AlbumCard
        v-for="b in savedArtists"
        :key="b.id"
        :title="b.title"
        :artwork-url="null"
        :clickable="true"
        @click="openArtist(b.musicbrainz_id)"
      />
    </div>
  </div>
</template>

<style scoped>
</style>
