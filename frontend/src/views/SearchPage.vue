<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Loading, Plus, Check, MoreFilled } from '@element-plus/icons-vue'
import { searchService, type GlobalSearchCategory, type GlobalSearchItem, type SearchProvider } from '@/api/services/searchService'
import { bookmarkService } from '@/api/services/bookmarkService'
import { songService } from '@/api/services/songService'
import { ElMessage } from 'element-plus'
import SongRow from '@/components/SongRow.vue'
import AlbumCard from '@/components/AlbumCard.vue'

const router = useRouter()

const activeTab = ref<GlobalSearchCategory>('songs')
const provider = ref<SearchProvider>('musicbrainz')
const query = ref('')
const isLoading = ref(false)
const items = ref<GlobalSearchItem[]>([])
const total = ref(0)
const offset = ref(0)
const limit = 25
let searchRequestId = 0

const providers: { value: SearchProvider; label: string }[] = [
  { value: 'musicbrainz', label: 'MusicBrainz' },
  { value: 'itunes', label: 'iTunes' },
  { value: 'deezer', label: 'Deezer' },
]

async function runSearch() {
  if (!query.value.trim()) {
    items.value = []
    total.value = 0
    return
  }
  const requestId = ++searchRequestId
  isLoading.value = true
  try {
    const res = await searchService.searchGlobal(
      query.value.trim(),
      activeTab.value,
      provider.value,
      offset.value,
      limit
    )
    if (requestId !== searchRequestId) return
    items.value = res.data.items ?? []
    total.value = res.data.total ?? 0
  } catch (e) {
    if (requestId !== searchRequestId) return
    console.error(e)
    items.value = []
    total.value = 0
  } finally {
    if (requestId === searchRequestId) isLoading.value = false
  }
}

async function toggleSave(item: GlobalSearchItem) {
  if (item.item_type === 'song') return
  const key = item.provider && item.provider !== 'musicbrainz'
    ? `${item.provider}:${String(item.id)}`
    : String(item.id)
  if (item.is_saved) {
    try {
      const check = await bookmarkService.check(
        item.item_type as 'artist' | 'album',
        key
      )
      if (check.data?.id) {
        await bookmarkService.delete(check.data.id)
        item.is_saved = false
        ElMessage.success('Removed from saved')
      }
    } catch {
      ElMessage.error('Error removing bookmark')
    }
    return
  }
  try {
    const title = item.item_type === 'artist' ? item.name : item.title
    await bookmarkService.create({
      bookmark_type: item.item_type as 'artist' | 'album',
      musicbrainz_id: key,
      title: title || '',
    })
    item.is_saved = true
    ElMessage.success('Added to saved')
  } catch {
    ElMessage.error('Error saving')
  }
}

function goToArtist(id: string) {
  router.push(`/artists/${id}`)
}

function goToRelease(id: string) {
  router.push(`/releases/${id}`)
}

const addingSongId = ref<string | number | null>(null)
async function addSongToLibrary(item: GlobalSearchItem) {
  if (item.item_type !== 'song' || !item.preview_url) {
    ElMessage.warning('No preview available to add')
    return
  }
  addingSongId.value = item.id
  try {
    await songService.createFromPreview({
      preview_url: item.preview_url,
      title: item.title || 'Unknown',
      artist: item.artist || 'Unknown',
      album: item.album || undefined,
    })
    ElMessage.success('Added to your library')
  } catch {
    ElMessage.error('Failed to add to library')
  } finally {
    addingSongId.value = null
  }
}

function downloadSong(item: GlobalSearchItem) {
  if (item.item_type !== 'song' || !item.preview_url) {
    ElMessage.warning('No preview available to download')
    return
  }
  const url = songService.getDownloadExternalUrl(item.preview_url)
  window.open(url, '_blank', 'noopener')
}

const tabs = [
  { value: 'songs' as GlobalSearchCategory, label: 'Songs' },
  { value: 'albums' as GlobalSearchCategory, label: 'Albums' },
  { value: 'artists' as GlobalSearchCategory, label: 'Artists' },
]

function formatDuration(ms: number | null | undefined): string {
  if (ms == null || ms < 0) return '—'
  const sec = Math.floor(ms / 1000)
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

const audio = new Audio()
audio.preload = 'none'
const playingKey = ref<string | null>(null)
const isPlaying = ref(false)

function itemKey(item: GlobalSearchItem): string {
  return `${item.provider || ''}:${String(item.id)}`
}

async function togglePlay(item: GlobalSearchItem) {
  if (!item.preview_url) return
  const key = itemKey(item)
  try {
    if (playingKey.value === key && isPlaying.value) {
      audio.pause()
      isPlaying.value = false
      return
    }
    if (audio.src !== item.preview_url) {
      audio.src = item.preview_url
    }
    playingKey.value = key
    await audio.play()
    isPlaying.value = true
  } catch {
    ElMessage.error('Playback failed')
  }
}

audio.addEventListener('ended', () => {
  isPlaying.value = false
})
audio.addEventListener('pause', () => {
  isPlaying.value = false
})
audio.addEventListener('play', () => {
  isPlaying.value = true
})

watch([activeTab, query, provider], () => {
  offset.value = 0
  audio.pause()
  audio.src = ''
  playingKey.value = null
  runSearch()
})

onBeforeUnmount(() => {
  audio.pause()
  audio.src = ''
})
</script>

<template>
  <div class="search-page w-full h-full flex flex-col gap-4">
    <h1 class="text-2xl font-bold text-stone-100">Search</h1>

    <div class="flex gap-2 items-center flex-wrap">
      <div class="relative flex-1 min-w-[200px] max-w-md">
        <el-input
          v-model="query"
          placeholder="Songs, albums, artists..."
          clearable
          class="w-full search-input"
          @keyup.enter="runSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <el-button class="search-btn" :loading="isLoading" @click="runSearch">
        Search
      </el-button>
    </div>

    <div class="flex flex-wrap gap-2 items-center">
      <span class="text-sm text-stone-400">Source:</span>
      <select
        v-model="provider"
        class="provider-select px-3 py-2 rounded-lg border border-stone-600 bg-stone-800 text-stone-200 text-sm"
      >
        <option v-for="p in providers" :key="p.value" :value="p.value">{{ p.label }}</option>
      </select>
    </div>
    <div class="flex gap-2 p-1 bg-stone-800/80 rounded-lg">
      <button
        v-for="t in tabs"
        :key="t.value"
        :class="[
          'px-4 py-2 rounded-md font-medium transition-all cursor-pointer',
          activeTab === t.value
            ? 'bg-amber-800/90 text-amber-100 shadow-sm'
            : 'text-stone-400 hover:text-stone-200'
        ]"
        @click="activeTab = t.value"
      >
        {{ t.label }}
      </button>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div v-if="isLoading" class="flex justify-center items-center py-12">
        <el-icon class="is-loading" :size="36"><Loading /></el-icon>
      </div>
      <div v-else-if="!query.trim()" class="text-center py-12 text-stone-500">
        Enter a query and click Search
      </div>
      <div v-else-if="items.length === 0" class="text-center py-12 text-stone-500">
        No results found
      </div>
      <div v-else class="flex flex-col">
        <template v-if="activeTab === 'songs'">
          <SongRow
            v-for="item in items"
            :key="String(item.id) + (item.provider || '')"
            :title="item.title || 'Untitled'"
            :subtitle="item.artist || '—'"
            :artwork-url="item.artwork_url"
            :duration-text="formatDuration(item.duration_ms)"
            :active="playingKey === `${item.provider || ''}:${String(item.id)}` && isPlaying"
            @click="togglePlay(item)"
          >
            <template #actions>
              <el-dropdown
                trigger="click"
                @command="(cmd: string) => cmd === 'add' ? addSongToLibrary(item) : downloadSong(item)"
              >
                <button
                  type="button"
                  class="p-1.5 rounded hover:bg-stone-700 text-stone-400 hover:text-stone-200 transition-colors"
                  aria-label="Actions"
                >
                  <el-icon :size="18"><MoreFilled /></el-icon>
                </button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :disabled="!item.preview_url" :command="'add'">
                      Add to my library
                    </el-dropdown-item>
                    <el-dropdown-item :disabled="!item.preview_url" :command="'download'">
                      Download to device
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </SongRow>
        </template>

        <template v-else-if="activeTab === 'albums'">
          <div class="flex flex-wrap gap-4 pb-2">
            <AlbumCard
              v-for="item in items"
              :key="String(item.id) + (item.provider || '')"
              :title="item.title || 'Untitled'"
              :subtitle="item.artist || '—'"
              :artwork-url="item.artwork_url"
              :clickable="true"
              @click="item.provider === 'musicbrainz' ? goToRelease(String(item.id)) : router.push(`/albums/${item.provider}/${String(item.id)}`)"
            >
              <template #badge>
                <el-button
                  :type="item.is_saved ? 'success' : 'default'"
                  size="small"
                  class="album-save-btn"
                  @click.stop="toggleSave(item)"
                >
                  <el-icon v-if="item.is_saved"><Check /></el-icon>
                  <el-icon v-else><Plus /></el-icon>
                </el-button>
              </template>
            </AlbumCard>
          </div>
        </template>

        <template v-else-if="activeTab === 'artists'">
          <div
            v-for="item in items"
            :key="String(item.id) + (item.provider || '')"
            class="p-4 rounded-lg border border-stone-600 bg-stone-800/80 flex justify-between items-center"
          >
            <div
              :class="['flex-1 min-w-0', item.provider === 'musicbrainz' ? 'cursor-pointer' : '']"
              @click="item.provider === 'musicbrainz' && goToArtist(String(item.id))"
            >
              <h3 class="font-semibold text-lg text-stone-100">{{ item.name || '—' }}</h3>
              <p v-if="item.country" class="text-sm text-stone-400">{{ item.country }}</p>
              <p v-if="item.disambiguation" class="text-xs text-stone-500">{{ item.disambiguation }}</p>
            </div>
            <el-button
              v-if="item.provider === 'musicbrainz'"
              :type="item.is_saved ? 'success' : 'default'"
              size="small"
              class="artist-save-btn"
              @click="toggleSave(item)"
            >
              <el-icon v-if="item.is_saved"><Check /></el-icon>
              <el-icon v-else><Plus /></el-icon>
              <span class="ml-1">{{ item.is_saved ? 'Saved' : 'Save' }}</span>
            </el-button>
          </div>
        </template>
      </div>

      <p v-if="total > limit && items.length" class="text-sm text-stone-500 mt-2">
        Showing {{ items.length }} of {{ total }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.search-page {
  background: linear-gradient(180deg, #1c1917 0%, #292524 100%);
  color: #fafaf9;
}

.search-input :deep(.el-input__wrapper) {
  background-color: #292524;
  border-color: #57534e;
  box-shadow: 0 0 0 1px #57534e;
}
.search-input :deep(.el-input__wrapper:hover),
.search-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #a8a29e;
}
.search-input :deep(.el-input__inner) {
  color: #fafaf9;
}
.search-input :deep(.el-input__inner::placeholder) {
  color: #78716c;
}

.search-btn {
  background-color: #b45309 !important;
  border-color: #b45309 !important;
  color: #fef3c7 !important;
}
.search-btn:hover {
  background-color: #c2410c !important;
  border-color: #c2410c !important;
  color: #fef3c7 !important;
}

.album-save-btn:not(.el-button--success),
.artist-save-btn:not(.el-button--success) {
  background-color: #57534e !important;
  border-color: #57534e !important;
  color: #fafaf9 !important;
}
.album-save-btn:not(.el-button--success):hover,
.artist-save-btn:not(.el-button--success):hover {
  background-color: #b45309 !important;
  border-color: #b45309 !important;
}
</style>
