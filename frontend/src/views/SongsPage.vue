<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useSongStore } from '@/stores/song'
import { useRouter } from 'vue-router'
import { Loading, MoreFilled } from '@element-plus/icons-vue'
import { AppRoutes } from '@/constants/appRoutes'
import { ElMessage, ElMessageBox } from 'element-plus'
import { songService } from '@/api/services/songService'
import SongRow from '@/components/SongRow.vue'

const songStore = useSongStore()
const router = useRouter()

const songs = computed(() => songStore.songs)
const isLoading = computed(() => songStore.isLoading)
const playingId = ref<number | null>(null)
const isPlaying = ref(false)

const audio = new Audio()
audio.preload = 'none'
audio.addEventListener('ended', () => {
  isPlaying.value = false
  playingId.value = null
})
audio.addEventListener('pause', () => {
  isPlaying.value = false
})
audio.addEventListener('play', () => {
  isPlaying.value = true
})

function onAddSongClick() {
  router.push(AppRoutes.CREATE_SONG)
}

async function togglePlay(songId: number) {
  const url = songStore.getStreamUrl(songId)
  try {
    if (playingId.value === songId && isPlaying.value) {
      audio.pause()
      return
    }
    if (audio.src !== url) {
      audio.src = url
    }
    playingId.value = songId
    await audio.play()
  } catch {
    ElMessage.error('Playback failed')
  }
}

function downloadSong(songId: number) {
  const url = songService.getDownloadUrl(songId)
  window.open(url, '_blank', 'noopener')
}

async function deleteSong(songId: number) {
  try {
    await ElMessageBox.confirm(
      'Delete this song from your library?',
      'Confirm',
      { type: 'warning', confirmButtonText: 'Delete', cancelButtonText: 'Cancel' }
    )
  } catch {
    return
  }
  try {
    await songStore.deleteSong(songId)
    if (playingId.value === songId) {
      audio.pause()
      audio.src = ''
      playingId.value = null
    }
    ElMessage.success('Deleted')
  } catch {
    ElMessage.error('Delete failed')
  }
}

function formatDurationPlaceholder(): string {
  return '—'
}

onMounted(() => {
  songStore.fetchSongs()
})

onBeforeUnmount(() => {
  audio.pause()
  audio.src = ''
})
</script>

<template>
  <div class="songs-page w-full h-full relative flex flex-col gap-4">
    <h1 class="text-2xl font-bold text-stone-100">My songs</h1>

    <div class="flex flex-col h-full overflow-y-auto">
      <div v-if="isLoading" class="flex justify-center items-center flex-1">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      </div>
      <div v-else-if="songs.length === 0" class="flex flex-col justify-center items-center flex-1 text-stone-500">
        <p class="text-lg">No songs</p>
        <p class="text-sm">Add your first song to get started</p>
      </div>
      <div v-else class="flex flex-col">
        <SongRow
          v-for="song in songs"
          :key="song.id"
          :title="song.title || 'Untitled'"
          :subtitle="song.artist || 'Unknown artist'"
          :duration-text="formatDurationPlaceholder()"
          :active="playingId === song.id && isPlaying"
          @click="togglePlay(song.id)"
        >
          <template #actions>
            <el-dropdown
              trigger="click"
              @command="(cmd: string) => cmd === 'download' ? downloadSong(song.id) : cmd === 'delete' ? deleteSong(song.id) : togglePlay(song.id)"
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
                  <el-dropdown-item :command="'play'">
                    {{ playingId === song.id && isPlaying ? 'Pause' : 'Play' }}
                  </el-dropdown-item>
                  <el-dropdown-item :command="'download'">
                    Download
                  </el-dropdown-item>
                  <el-dropdown-item :command="'delete'" divided>
                    Delete
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </SongRow>
      </div>
    </div>

    <button
      @click="onAddSongClick"
      class="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-amber-700 hover:bg-amber-600 text-amber-50 shadow-lg flex items-center justify-center transition-all z-50"
    >
      <span class="text-2xl font-bold">+</span>
    </button>
  </div>
</template>

<style scoped>
.songs-page {
  background: linear-gradient(180deg, #1c1917 0%, #292524 100%);
  color: #fafaf9;
}
</style>

