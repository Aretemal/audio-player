<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Loading, MoreFilled, Plus, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import SongRow from '@/components/SongRow.vue'
import { searchService, type SearchProvider } from '@/api/services/searchService'
import { bookmarkService } from '@/api/services/bookmarkService'
import { songService } from '@/api/services/songService'

const route = useRoute()
const provider = computed(() => route.params.provider as SearchProvider)
const albumId = computed(() => route.params.id as string)

const isLoading = ref(false)
const album = ref<{
  id: string
  title?: string
  artist?: string
  artwork_url?: string | null
  provider: SearchProvider
  is_saved: boolean
  bookmark_key: string
  tracks: Array<{
    id: string
    title?: string
    artist?: string | null
    duration_ms?: number | null
    preview_url?: string | null
    track_number?: number | null
  }>
} | null>(null)

function formatDuration(ms: number | null | undefined): string {
  if (ms == null || ms < 0) return '—'
  const sec = Math.floor(ms / 1000)
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

const audio = new Audio()
audio.preload = 'none'
const playingTrackId = ref<string | null>(null)
const isPlaying = ref(false)

async function togglePlay(track: { id: string; preview_url?: string | null }, key: string) {
  if (!track.preview_url) return
  try {
    if (playingTrackId.value === key && isPlaying.value) {
      audio.pause()
      return
    }
    if (audio.src !== track.preview_url) {
      audio.src = track.preview_url
    }
    playingTrackId.value = key
    await audio.play()
  } catch {
    ElMessage.error('Playback failed')
  }
}

audio.addEventListener('ended', () => {
  isPlaying.value = false
  playingTrackId.value = null
})
audio.addEventListener('pause', () => {
  isPlaying.value = false
})
audio.addEventListener('play', () => {
  isPlaying.value = true
})

async function load() {
  isLoading.value = true
  try {
    const res = await searchService.albumDetail(provider.value, albumId.value)
    album.value = res.data
  } catch {
    album.value = null
  } finally {
    isLoading.value = false
  }
}

async function toggleAlbumSave() {
  if (!album.value) return
  try {
    if (album.value.is_saved) {
      const check = await bookmarkService.check('album', album.value.bookmark_key)
      if (check.data?.id) {
        await bookmarkService.delete(check.data.id)
        album.value.is_saved = false
        ElMessage.success('Removed from saved')
      }
      return
    }
    await bookmarkService.create({
      bookmark_type: 'album',
      musicbrainz_id: album.value.bookmark_key,
      title: `${album.value.title || 'Untitled'}${album.value.artist ? ' — ' + album.value.artist : ''}`,
    })
    album.value.is_saved = true
    ElMessage.success('Saved')
  } catch {
    ElMessage.error('Save failed')
  }
}

async function addTrackToLibrary(track: { title?: string; artist?: string | null; preview_url?: string | null }) {
  if (!track.preview_url) {
    ElMessage.warning('No preview available to add')
    return
  }
  try {
    await songService.createFromPreview({
      preview_url: track.preview_url,
      title: track.title || 'Unknown',
      artist: track.artist || album.value?.artist || 'Unknown',
      album: album.value?.title,
    })
    ElMessage.success('Added to your library')
  } catch {
    ElMessage.error('Failed to add')
  }
}

function downloadTrack(track: { preview_url?: string | null }) {
  if (!track.preview_url) {
    ElMessage.warning('No preview available to download')
    return
  }
  const url = songService.getDownloadExternalUrl(track.preview_url)
  window.open(url, '_blank', 'noopener')
}

async function addAllPreviews() {
  if (!album.value) return
  const tracks = album.value.tracks.filter(t => !!t.preview_url)
  if (tracks.length === 0) {
    ElMessage.warning('No previews to add')
    return
  }
  for (const t of tracks) {
    // best-effort; ignore per-track errors
    try {
      await songService.createFromPreview({
        preview_url: t.preview_url as string,
        title: t.title || 'Unknown',
        artist: t.artist || album.value.artist || 'Unknown',
        album: album.value.title,
      })
    } catch {
      // ignore
    }
  }
  ElMessage.success('Added previews to your library')
}

onMounted(load)
onBeforeUnmount(() => {
  audio.pause()
  audio.src = ''
})
</script>

<template>
  <div class="album-detail w-full h-full overflow-y-auto p-6">
    <div v-if="isLoading" class="flex justify-center items-center py-20">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>

    <div v-else-if="album" class="space-y-6">
      <div class="flex flex-col md:flex-row gap-5 items-start">
        <div class="w-44 h-44 rounded-xl overflow-hidden bg-stone-700/60 border border-stone-600 shrink-0">
          <img
            v-if="album.artwork_url"
            :src="album.artwork_url"
            :alt="album.title || ''"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-stone-500 text-3xl">♪</div>
        </div>

        <div class="min-w-0 flex-1">
          <h1 class="text-2xl md:text-3xl font-bold text-stone-100 truncate">
            {{ album.title || 'Untitled' }}
          </h1>
          <p class="text-stone-400 mt-1 truncate">{{ album.artist || '—' }}</p>
          <p class="text-xs text-stone-500 mt-1 capitalize">{{ album.provider }}</p>

          <div class="mt-4 flex flex-wrap gap-2">
            <el-button
              class="search-btn"
              :type="album.is_saved ? 'success' : 'default'"
              @click="toggleAlbumSave"
            >
              <el-icon v-if="album.is_saved"><Check /></el-icon>
              <el-icon v-else><Plus /></el-icon>
              <span class="ml-1">{{ album.is_saved ? 'Saved' : 'Save' }}</span>
            </el-button>

            <el-button class="search-btn" type="default" @click="addAllPreviews">
              Add all previews to library
            </el-button>
          </div>
        </div>
      </div>

      <div>
        <h2 class="text-lg font-semibold text-stone-100 mb-3">Tracks</h2>

        <div v-if="album.tracks.length === 0" class="text-stone-500">
          No tracks
        </div>

        <div v-else class="flex flex-col">
          <SongRow
            v-for="t in album.tracks"
            :key="t.id"
            :title="t.title || 'Untitled'"
            :subtitle="t.artist || album.artist || '—'"
            :duration-text="formatDuration(t.duration_ms)"
            :active="playingTrackId === `${album.provider}:${t.id}` && isPlaying"
            @click="togglePlay(t, `${album.provider}:${t.id}`)"
          >
            <template #actions>
              <el-dropdown
                trigger="click"
                @command="(cmd: string) => cmd === 'add' ? addTrackToLibrary(t) : downloadTrack(t)"
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
                    <el-dropdown-item :disabled="!t.preview_url" :command="'add'">
                      Add to my library
                    </el-dropdown-item>
                    <el-dropdown-item :disabled="!t.preview_url" :command="'download'">
                      Download to device
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </SongRow>
        </div>
      </div>
    </div>

    <div v-else class="text-stone-500 py-20 text-center">
      Album not found
    </div>
  </div>
</template>

<style scoped>
.album-detail {
  background: linear-gradient(180deg, #1c1917 0%, #292524 100%);
  color: #fafaf9;
}
</style>

