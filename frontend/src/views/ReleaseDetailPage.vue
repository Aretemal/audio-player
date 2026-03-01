<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { releaseService } from '@/api/services/releaseService'
import { bookmarkService } from '@/api/services/bookmarkService'
import type { Release } from '@/api/types/release'
import type { Bookmark, BookmarkCategory } from '@/api/types/bookmark'
import { Loading } from '@element-plus/icons-vue'
import { ElButton, ElDialog, ElSelect, ElOption, ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const releaseId = computed(() => route.params.id as string)

const release = ref<Release | null>(null)
const isLoading = ref(false)
const bookmark = ref<Bookmark | null>(null)
const categories = ref<BookmarkCategory[]>([])
const showBookmarkDialog = ref(false)
const selectedCategories = ref<number[]>([])
const newCategoryName = ref('')
const showNewCategory = ref(false)

async function loadRelease() {
  isLoading.value = true
  try {
    const response = await releaseService.getById(releaseId.value)
    release.value = response.data
    await checkBookmark()
  } catch (error) {
    console.error('Error loading release:', error)
  } finally {
    isLoading.value = false
  }
}

async function loadCategories() {
  try {
    const response = await bookmarkService.getCategories()
    categories.value = response.data
  } catch (error) {
    console.error('Error loading categories:', error)
  }
}

async function checkBookmark() {
  if (!release.value) return
  try {
    const response = await bookmarkService.check('album', release.value.id)
    bookmark.value = response.data || null
    if (bookmark.value) {
      selectedCategories.value = bookmark.value.categories.map(c => c.id)
    }
  } catch (error) {
    console.error('Error checking bookmark:', error)
  }
}

async function toggleBookmark() {
  if (bookmark.value) {
    try {
      await bookmarkService.delete(bookmark.value.id)
      bookmark.value = null
      ElMessage.success('Bookmark removed')
    } catch (error) {
      ElMessage.error('Error removing bookmark')
    }
  } else {
    await loadCategories()
    showBookmarkDialog.value = true
  }
}

async function saveBookmark() {
  if (!release.value) return
  
  try {
    const response = await bookmarkService.create({
      bookmark_type: 'album',
      musicbrainz_id: release.value.id,
      title: release.value.title,
      category_ids: selectedCategories.value,
    })
    bookmark.value = response.data
    showBookmarkDialog.value = false
    ElMessage.success('Bookmark added')
  } catch (error) {
    ElMessage.error('Error creating bookmark')
  }
}

async function createCategory() {
  if (!newCategoryName.value.trim()) return
  
  try {
    const response = await bookmarkService.createCategory({ name: newCategoryName.value })
    categories.value.push(response.data)
    selectedCategories.value.push(response.data.id)
    newCategoryName.value = ''
    showNewCategory.value = false
    ElMessage.success('Category created')
  } catch (error) {
    ElMessage.error('Error creating category')
  }
}

function formatDuration(ms: number | null | undefined): string {
  if (!ms) return ''
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

function goToArtist(artistId: string) {
  router.push(`/artists/${artistId}`)
}

onMounted(() => {
  loadRelease()
})
</script>

<template>
  <div class="w-full h-full overflow-y-auto">
    <div v-if="isLoading" class="flex justify-center items-center py-20">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>
    
    <div v-else-if="release" class="p-6 space-y-6">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-3xl font-bold dark:text-white mb-2">{{ release.title }}</h1>
          <div v-if="release.artists && release.artists.length > 0" class="mt-2">
            <span
              v-for="(artist, index) in release.artists"
              :key="artist.id"
              @click="goToArtist(artist.id)"
              class="text-lg text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 cursor-pointer"
            >
              {{ artist.name }}<span v-if="index < release.artists!.length - 1">, </span>
            </span>
          </div>
        </div>
        <ElButton
          :type="bookmark ? 'success' : 'primary'"
          @click="toggleBookmark"
        >
          {{ bookmark ? '★ In bookmarks' : '☆ Add to bookmarks' }}
        </ElButton>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-if="release.date" class="text-sm">
          <span class="font-medium dark:text-gray-300">Release date:</span>
          <span class="ml-2 dark:text-gray-400">{{ release.date }}</span>
        </div>
        <div v-if="release.country" class="text-sm">
          <span class="font-medium dark:text-gray-300">Country:</span>
          <span class="ml-2 dark:text-gray-400">{{ release.country }}</span>
        </div>
        <div v-if="release.status" class="text-sm">
          <span class="font-medium dark:text-gray-300">Status:</span>
          <span class="ml-2 dark:text-gray-400">{{ release.status }}</span>
        </div>
      </div>

      <div v-if="release.tracks && release.tracks.length > 0">
        <h2 class="text-2xl font-semibold dark:text-white mb-4">Tracks</h2>
        <div class="space-y-2">
          <div
            v-for="track in release.tracks"
            :key="track.id"
            class="p-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"
          >
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-3">
                <span v-if="track.position" class="text-gray-500 dark:text-gray-400 w-8">
                  {{ track.position }}.
                </span>
                <span class="dark:text-white">{{ track.title }}</span>
              </div>
              <span v-if="track.length" class="text-sm text-gray-500 dark:text-gray-400">
                {{ formatDuration(track.length) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <ElDialog v-model="showBookmarkDialog" title="Add to bookmarks" width="400px">
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-2 dark:text-gray-300">Categories</label>
        <ElSelect
          v-model="selectedCategories"
          multiple
          placeholder="Select categories"
          class="w-full"
        >
          <ElOption
            v-for="category in categories"
            :key="category.id"
            :label="category.name"
            :value="category.id"
          />
        </ElSelect>
      </div>
      
      <div v-if="showNewCategory" class="space-y-2">
        <label class="block text-sm font-medium dark:text-gray-300">New category</label>
        <div class="flex gap-2">
          <input
            v-model="newCategoryName"
            type="text"
            placeholder="Category name"
            class="flex-1 px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600"
            @keyup.enter="createCategory"
          />
          <ElButton @click="createCategory">Create</ElButton>
        </div>
      </div>
      
      <ElButton
        type="text"
        @click="showNewCategory = !showNewCategory"
        class="w-full"
      >
        {{ showNewCategory ? 'Cancel' : '+ Create new category' }}
      </ElButton>
    </div>
    
    <template #footer>
      <ElButton @click="showBookmarkDialog = false">Cancel</ElButton>
      <ElButton type="primary" @click="saveBookmark">Save</ElButton>
    </template>
  </ElDialog>
</template>

<style scoped>
</style>
