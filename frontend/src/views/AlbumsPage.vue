<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { ElNotification } from 'element-plus'
import apiClient from '@/api/client'
import { bookmarkService } from '@/api/services/bookmarkService'
import type { Album } from '@/api/types/album'
import type { Bookmark } from '@/api/types/bookmark'
import AlbumCard from '@/components/AlbumCard.vue'

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
  if (mbid.includes(':')) {
    const [provider, id] = mbid.split(':', 2)
    router.push(`/albums/${provider}/${id}`)
    return
  }
  router.push(`/releases/${mbid}`)
}

onMounted(() => {
  fetchAlbums()
})
</script>

<template>
  <div class="w-full h-full flex flex-col gap-6">
    <h1 class="text-2xl font-bold text-stone-100">My Albums</h1>
    <p class="text-stone-400">
      Albums from your collection and saved releases from search.
    </p>

    <div v-if="isLoading" class="flex justify-center items-center py-12">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>

    <template v-else>
      <section v-if="albums.length > 0">
        <h2 class="text-lg font-semibold text-stone-100 mb-3">Collection</h2>
        <div class="flex flex-wrap gap-4">
          <AlbumCard
            v-for="album in albums"
            :key="album.id"
            :title="album.title || 'Untitled'"
            :subtitle="album.creator || 'Unknown'"
            :artwork-url="null"
            :clickable="false"
          >
            <template #badge>
              <span class="px-2 py-0.5 rounded-full bg-stone-700/80 text-xs text-stone-200">
                {{ album.song_ids?.length || 0 }} tracks
              </span>
            </template>
          </AlbumCard>
        </div>
        <p class="mt-2 text-xs text-stone-500">
          Created dates: from {{ albums[0] && formatDate(albums[0].created_at) }} (first album)
        </p>
      </section>

      <section v-if="savedReleases.length > 0">
        <h2 class="text-lg font-semibold text-stone-100 mb-3">Saved Releases</h2>
        <div class="flex flex-wrap gap-4">
          <AlbumCard
            v-for="b in savedReleases"
            :key="b.id"
            :title="b.title"
            :artwork-url="null"
            :clickable="true"
            @click="openRelease(b.musicbrainz_id)"
          />
        </div>
      </section>

      <div
        v-if="albums.length === 0 && savedReleases.length === 0"
        class="flex flex-col justify-center items-center py-20 text-stone-500"
      >
        <p class="text-lg">No albums</p>
        <p class="text-sm">Add songs to your collection or save releases from Search</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
</style>
