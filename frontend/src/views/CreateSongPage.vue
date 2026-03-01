<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSongStore } from '@/stores/song'
import { useRouter } from 'vue-router'
import type { SongCreate } from '@/api/types/song'
import { ElNotification } from 'element-plus'
import { Close, Plus } from '@element-plus/icons-vue'
import { AppRoutes } from '@/constants/appRoutes'

const songStore = useSongStore()
const router = useRouter()

const formRef = ref()
const fileInputRef = ref<HTMLInputElement | null>(null)

const type = ref<'track' | 'album'>('track')

const form = ref<SongCreate>({
  title: '',
  artist: '',
  album: '',
  file: null as any,
})

const albumForm = ref({
  name: '',
  author: '',
  songs: [] as Array<{
    file: File | null
    title: string
    artist: string
    fileName: string
  }>,
})

const selectedFileName = ref<string>('')

const isFormValid = computed(() => {
  if (type.value === 'track') {
    return form.value.file !== null
  } else {
    return albumForm.value.name !== '' &&
           albumForm.value.author !== '' &&
           albumForm.value.songs.length > 0 &&
           albumForm.value.songs.every(s => s.file !== null)
  }
})

const rules = {
  file: [{
    required: true,
    message: 'File is required',
    trigger: 'change',
  }],
}

function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    form.value.file = target.files[0]
    selectedFileName.value = target.files[0].name
  }
}

function onFileRemove() {
  form.value.file = null as any
  selectedFileName.value = ''
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

function addAlbumSong() {
  albumForm.value.songs.push({
    file: null,
    title: '',
    artist: '',
    fileName: '',
  })
}

function onTypeChange() {
  resetForm()
  if (type.value === 'album' && albumForm.value.songs.length === 0) {
    addAlbumSong()
  }
}

function removeAlbumSong(index: number) {
  albumForm.value.songs.splice(index, 1)
}

function onAlbumSongFileChange(event: Event, index: number) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const file = target.files[0]
    if (file) {
      albumForm.value.songs[index].file = file
      albumForm.value.songs[index].fileName = file.name
    }
  }
}

function triggerAlbumSongFileInput(index: number) {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'audio/*'
  input.onchange = (e: Event) => onAlbumSongFileChange(e, index)
  input.click()
}

function resetForm() {
  form.value = {
    title: '',
    artist: '',
    album: '',
    file: null as any,
  }
  albumForm.value = {
    name: '',
    author: '',
    songs: [],
  }
  selectedFileName.value = ''
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
  formRef.value?.resetFields()
}

async function onSubmit() {
  if (type.value === 'track') {
    if (!form.value.file) {
      ElNotification({
        message: 'Please select a file',
        type: 'warning',
        duration: 3000,
      })
      return
    }

    try {
      await songStore.createSong(form.value)

      if (songStore.error) {
        ElNotification({
          message: songStore.error,
          type: 'error',
          duration: 3000,
        })
      } else {
      ElNotification({
        message: 'Song added successfully!',
        type: 'success',
        duration: 3000,
      })
      await songStore.fetchSongs()
      router.push(AppRoutes.SONGS)
      }
    } catch (error) {
      ElNotification({
        message: 'Error adding song',
        type: 'error',
        duration: 3000,
      })
    }
  } else {
    if (albumForm.value.songs.length === 0) {
      ElNotification({
        message: 'Add at least one song to the album',
        type: 'warning',
        duration: 3000,
      })
      return
    }

    try {
      for (const song of albumForm.value.songs) {
        if (!song.file) continue

        await songStore.createSong({
          title: song.title || undefined,
          artist: song.artist || albumForm.value.author || undefined,
          album: albumForm.value.name,
          file: song.file,
        })
      }

      ElNotification({
        message: 'Album created successfully!',
        type: 'success',
        duration: 3000,
      })
      await songStore.fetchSongs()
      router.push(AppRoutes.SONGS)
    } catch (error) {
      ElNotification({
        message: 'Error creating album',
        type: 'error',
        duration: 3000,
      })
    }
  }
}

function onCancel() {
  router.push(AppRoutes.SONGS)
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6 flex gap-2 bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
      <button
        @click="type = 'track'; onTypeChange()"
        :class="[
          'flex-1 px-4 py-2.5 rounded-md font-medium transition-all duration-200 cursor-pointer',
          type === 'track'
            ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
        ]"
      >
        Track
      </button>
      <button
        @click="type = 'album'; onTypeChange()"
        :class="[
          'flex-1 px-4 py-2.5 rounded-md font-medium transition-all duration-200 cursor-pointer',
          type === 'album'
            ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
        ]"
      >
        Album
      </button>
    </div>

    <div class="space-y-6">
      <template v-if="type === 'track'">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="space-y-5">
          <el-form-item prop="file" required>
            <div
              @click="() => fileInputRef?.click?.()"
              class="relative w-full border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20"
              :class="selectedFileName ? 'border-blue-400 dark:border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-300 dark:border-gray-600'"
            >
              <input
                ref="fileInputRef"
                type="file"
                accept="audio/*"
                class="hidden"
                @change="onFileChange"
              />
              <div v-if="!selectedFileName" class="space-y-2">
                <div class="text-4xl mb-2">🎵</div>
                <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Click to select file</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">or drag and drop here</p>
              </div>
              <div v-else class="flex items-center justify-center gap-3">
                <div class="text-2xl">✅</div>
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100 flex-1 truncate">{{ selectedFileName }}</span>
                <button
                  @click.stop="onFileRemove"
                  class="p-1.5 rounded-full hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                >
                  <el-icon class="text-red-500 dark:text-red-400"><Close /></el-icon>
                </button>
              </div>
            </div>
          </el-form-item>

          <div class="grid grid-cols-1 gap-5">
            <el-form-item prop="title">
              <el-input
                v-model="form.title"
                placeholder="Song title"
                size="large"
                class="rounded-lg"
              />
            </el-form-item>

            <el-form-item prop="artist">
              <el-input
                v-model="form.artist"
                placeholder="Artist"
                size="large"
                class="rounded-lg"
              />
            </el-form-item>
          </div>
        </el-form>
      </template>

      <template v-else>
        <el-form ref="formRef" label-position="top" class="space-y-5">
          <div class="grid grid-cols-1 gap-5">
            <el-form-item required>
              <el-input
                v-model="albumForm.name"
                placeholder="Album title"
                size="large"
                class="rounded-lg"
              />
            </el-form-item>

            <el-form-item required>
              <el-input
                v-model="albumForm.author"
                placeholder="Album artist"
                size="large"
                class="rounded-lg"
              />
            </el-form-item>
          </div>

          <el-form-item class="w-full">
            <div class="w-full space-y-4">
              <div
                v-for="(song, index) in albumForm.songs"
                :key="index"
                class="w-full p-5 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800/50 hover:shadow-md transition-all"
              >
                <div class="flex items-center justify-between mb-4">
                  <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">Track {{ index + 1 }}</span>
                  <button
                    type="button"
                    @click="removeAlbumSong(index)"
                    class="p-2 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors cursor-pointer"
                  >
                    <el-icon class="text-red-500 dark:text-red-400"><Close /></el-icon>
                  </button>
                </div>

                <div class="space-y-4">
                  <div
                    @click="triggerAlbumSongFileInput(index)"
                    class="w-full border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-all hover:border-blue-400 dark:hover:border-blue-500"
                    :class="song.fileName ? 'border-blue-400 dark:border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-300 dark:border-gray-600'"
                  >
                    <div v-if="!song.fileName" class="space-y-1">
                      <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Select audio file</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Click to select</p>
                    </div>
                    <div v-else class="flex items-center justify-center gap-2">
                      <div class="text-lg">✅</div>
                      <span class="text-sm font-medium text-gray-900 dark:text-gray-100 flex-1 truncate">{{ song.fileName }}</span>
                    </div>
                  </div>

                  <el-input
                    v-model="song.title"
                    placeholder="Song title (optional)"
                    size="default"
                    class="rounded-lg"
                  />

                  <el-input
                    v-model="song.artist"
                    placeholder="Artist (optional)"
                    size="default"
                    class="rounded-lg"
                  />
                </div>
              </div>

              <button
                type="button"
                @click="addAlbumSong"
                class="w-full p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all flex items-center justify-center gap-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 cursor-pointer"
              >
                <el-icon><Plus /></el-icon>
                <span class="font-medium">Add track</span>
              </button>
            </div>
          </el-form-item>
        </el-form>
      </template>

      <div class="flex justify-end gap-3 pt-4">
        <el-button
          @click="onCancel"
          size="large"
          class="rounded-lg"
        >
          Cancel
        </el-button>
        <el-button
          type="primary"
          :disabled="!isFormValid"
          :loading="songStore.isCreating"
          @click="onSubmit"
          size="large"
          class="rounded-lg px-8"
        >
          {{ type === 'track' ? 'Add track' : 'Create album' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>

