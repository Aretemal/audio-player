<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Close } from '@element-plus/icons-vue'
import { searchService } from '@/api/services/searchService'
import type { SearchResult, SearchCategory } from '@/api/types/search'
import { useSongStore } from '@/stores/song'
import { AppRoutes } from '@/constants/appRoutes'

const router = useRouter()
const songStore = useSongStore()

const searchQuery = ref('')
const isOpen = ref(false)
const isLoading = ref(false)
const searchResults = ref<SearchResult>({
  songs: [],
  albums: [],
  playlists: [],
  artists: [],
})

const selectedCategories = ref<SearchCategory[]>(['songs', 'albums', 'playlists', 'artists'])

const categories = [
  { value: 'songs' as SearchCategory, label: 'Songs' },
  { value: 'albums' as SearchCategory, label: 'Albums' },
  { value: 'playlists' as SearchCategory, label: 'Playlists' },
  { value: 'artists' as SearchCategory, label: 'Artists' },
]

const totalResults = computed(() => {
  return searchResults.value.songs.length +
    searchResults.value.albums.length +
    searchResults.value.playlists.length +
    searchResults.value.artists.length
})

const hasResults = computed(() => totalResults.value > 0)

const containerRef = ref<HTMLElement | null>(null)
const containerHeight = 400

const allResults = computed(() => {
  const items: Array<{ type: string; data: any; id: string | number }> = []
  
  if (selectedCategories.value.includes('songs')) {
    searchResults.value.songs.forEach(song => {
      items.push({ type: 'song', data: song, id: song.id })
    })
  }
  
  if (selectedCategories.value.includes('albums')) {
    searchResults.value.albums.forEach(album => {
      items.push({ type: 'album', data: album, id: album.id })
    })
  }
  
  if (selectedCategories.value.includes('playlists')) {
    searchResults.value.playlists.forEach(playlist => {
      items.push({ type: 'playlist', data: playlist, id: playlist.id })
    })
  }
  
  if (selectedCategories.value.includes('artists')) {
    searchResults.value.artists.forEach((artist, index) => {
      items.push({ type: 'artist', data: artist, id: `artist-${index}` })
    })
  }
  
  return items
})

function toggleCategory(category: SearchCategory) {
  const index = selectedCategories.value.indexOf(category)
  if (index > -1) {
    selectedCategories.value.splice(index, 1)
  } else {
    selectedCategories.value.push(category)
  }
}

async function performSearch() {
  if (!searchQuery.value.trim() || searchQuery.value.length < 1) {
    searchResults.value = {
      songs: [],
      albums: [],
      playlists: [],
      artists: [],
    }
    return
  }

  isLoading.value = true
  try {
    const response = await searchService.search(
      searchQuery.value,
      selectedCategories.value.length > 0 ? selectedCategories.value : undefined
    )
    searchResults.value = response.data
  } catch (error) {
    console.error('Search error:', error)
  } finally {
    isLoading.value = false
  }
}

function openSearch() {
  isOpen.value = true
  if (searchQuery.value) {
    performSearch()
  }
}

function closeSearch() {
  isOpen.value = false
  searchQuery.value = ''
  searchResults.value = {
    songs: [],
    albums: [],
    playlists: [],
    artists: [],
  }
}

function handleSongClick(songId: number) {
  router.push(AppRoutes.SONGS)
  closeSearch()
}

function handleAlbumClick(albumId: number) {
  router.push(AppRoutes.ALBUMS)
  closeSearch()
}

function handlePlaylistClick(playlistId: number) {
  router.push(AppRoutes.PLAYLISTS)
  closeSearch()
}

function handleArtistClick(artistName: string) {
  searchQuery.value = artistName
  selectedCategories.value = ['songs']
  performSearch()
}

let searchTimeout: ReturnType<typeof setTimeout> | null = null
watch(searchQuery, () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    if (isOpen.value) {
      performSearch()
    }
  }, 300)
})

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (containerRef.value && !containerRef.value.contains(target)) {
    closeSearch()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})
</script>

<template>
  <div ref="containerRef" class="relative">
    <button
      @click="openSearch"
      class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer"
      title="Search"
    >
      <el-icon :size="20" class="text-gray-600 dark:text-gray-300">
        <Search />
      </el-icon>
    </button>

    <div
      v-if="isOpen"
      class="absolute top-full right-0 mt-2 w-96 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50"
    >
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-lg dark:text-white">Search</h3>
          <button
            @click="closeSearch"
            class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
          >
            <el-icon :size="18"><Close /></el-icon>
          </button>
        </div>
        
        <div class="relative mb-3">
          <el-input
            v-model="searchQuery"
            placeholder="Search songs, albums, playlists, artists..."
            clearable
            @clear="searchResults = { songs: [], albums: [], playlists: [], artists: [] }"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="flex flex-wrap gap-2">
          <button
            v-for="category in categories"
            :key="category.value"
            @click="toggleCategory(category.value)"
            :class="[
              'px-3 py-1 rounded-md text-sm transition-all cursor-pointer',
              selectedCategories.includes(category.value)
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            ]"
          >
            {{ category.label }}
          </button>
        </div>
      </div>

      <div
        class="overflow-y-auto"
        :style="{ maxHeight: `${containerHeight}px` }"
      >
        <div v-if="isLoading" class="p-8 text-center text-gray-500 dark:text-gray-400">
          <el-icon class="is-loading" :size="24"><Search /></el-icon>
          <p class="mt-2">Searching...</p>
        </div>
        <div v-else-if="!hasResults && searchQuery" class="p-8 text-center text-gray-500 dark:text-gray-400">
          <p>No results found</p>
        </div>
        <div v-else-if="!searchQuery" class="p-8 text-center text-gray-500 dark:text-gray-400">
          <p>Enter a search query</p>
        </div>
        <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
          <div
            v-for="item in allResults"
            :key="`${item.type}-${item.id}`"
            @click="
              item.type === 'song' ? handleSongClick(item.data.id) :
              item.type === 'album' ? handleAlbumClick(item.data.id) :
              item.type === 'playlist' ? handlePlaylistClick(item.data.id) :
              handleArtistClick(item.data.name)
            "
            class="p-3 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
          >
            <div class="flex items-center gap-3">
              <div class="text-2xl">
                {{ item.type === 'song' ? '🎵' : item.type === 'album' ? '💿' : item.type === 'playlist' ? '📋' : '🎤' }}
              </div>
              <div class="flex-1 min-w-0">
                <h4 class="font-medium truncate dark:text-white">
                  {{ item.type === 'artist' ? item.data.name : (item.data.title || 'Untitled') }}
                </h4>
                <p class="text-sm text-gray-500 dark:text-gray-400 truncate">
                  <template v-if="item.type === 'song'">
                    {{ item.data.artist || 'Unknown artist' }}
                  </template>
                  <template v-else-if="item.type === 'album'">
                    Artist: {{ item.data.creator || 'Unknown' }}
                  </template>
                  <template v-else-if="item.type === 'playlist'">
                    Tracks: {{ item.data.song_ids?.length || 0 }}
                  </template>
                  <template v-else>
                    Tracks: {{ item.data.songs_count }}
                  </template>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="hasResults"
        class="p-3 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-500 dark:text-gray-400 text-center"
      >
        Found: {{ totalResults }}
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>

