<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSongStore } from '@/stores/song'
import type { SongCreate } from '@/api/types/song'
import { ElNotification } from 'element-plus'
import { Close } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'song-added': []
}>()

const songStore = useSongStore()

const formRef = ref()
const fileInputRef = ref<HTMLInputElement | null>(null)

const form = ref<SongCreate>({
  title: '',
  artist: '',
  playlist: '',
  album: '',
  file: null as any,
})

const selectedFileName = ref<string>('')

const isFormValid = computed(() => {
  return form.value.file !== null
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

function onDialogClose() {
  emit('update:modelValue', false)
  resetForm()
}

function resetForm() {
  form.value = {
    title: '',
    artist: '',
    playlist: '',
    album: '',
    file: null as any,
  }
  selectedFileName.value = ''
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
  formRef.value?.resetFields()
}

async function onSubmit() {
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
      emit('song-added')
      onDialogClose()
    }
  } catch (error) {
    ElNotification({
      message: 'Error adding song',
      type: 'error',
      duration: 3000,
    })
  }
}
</script>

<template>
  <el-dialog
    :model-value="modelValue"
    title="Add track"
    width="500px"
    @close="onDialogClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="Audio file" prop="file" required>
        <div class="flex flex-col gap-2">
          <el-button type="primary" @click="() => fileInputRef?.click?.()">
            Select file
          </el-button>
          <input
            ref="fileInputRef"
            type="file"
            accept="audio/*"
            class="hidden"
            @change="onFileChange"
          />
          <div v-if="selectedFileName" class="flex items-center gap-2 p-2 bg-gray-100 rounded">
            <span class="text-sm flex-1 truncate">{{ selectedFileName }}</span>
            <el-icon class="cursor-pointer" @click="onFileRemove"><Close /></el-icon>
          </div>
        </div>
      </el-form-item>

      <el-form-item label="Title" prop="title">
        <el-input
          v-model="form.title"
          placeholder="Enter song title"
        />
      </el-form-item>

      <el-form-item label="Artist" prop="artist">
        <el-input
          v-model="form.artist"
          placeholder="Enter artist name"
        />
      </el-form-item>

      <el-form-item label="Album" prop="album">
        <el-input
          v-model="form.album"
          placeholder="Enter album title"
        />
      </el-form-item>

      <el-form-item label="Playlist" prop="playlist">
        <el-input
          v-model="form.playlist"
          placeholder="Enter playlist name"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="flex justify-end gap-2">
        <el-button @click="onDialogClose">Cancel</el-button>
        <el-button
          type="primary"
          :disabled="!isFormValid"
          :loading="songStore.isCreating"
          @click="onSubmit"
        >
          Add
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
</style>

