<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { artistService } from '@/api/services/artistService'
import { bookmarkService } from '@/api/services/bookmarkService'
import type { ArtistDetail } from '@/api/types/artist'
import type { Bookmark, BookmarkCategory } from '@/api/types/bookmark'
import { Loading } from '@element-plus/icons-vue'
import { ElButton, ElDialog, ElSelect, ElOption, ElMessage } from 'element-plus'
import { AppRoutes } from '@/constants/appRoutes'

const route = useRoute()
const router = useRouter()
const artistId = computed(() => route.params.id as string)

const artist = ref<ArtistDetail | null>(null)
const isLoading = ref(false)
const bookmark = ref<Bookmark | null>(null)
const categories = ref<BookmarkCategory[]>([])
const showBookmarkDialog = ref(false)
const selectedCategories = ref<number[]>([])
const newCategoryName = ref('')
const showNewCategory = ref(false)

async function loadArtist() {
  isLoading.value = true
  try {
    const response = await artistService.getById(artistId.value)
    artist.value = response.data
    await checkBookmark()
  } catch (error) {
    console.error('Error loading artist:', error)
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
  if (!artist.value) return
  try {
    const response = await bookmarkService.check('artist', artist.value.id)
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
  if (!artist.value) return
  
  try {
    const response = await bookmarkService.create({
      bookmark_type: 'artist',
      musicbrainz_id: artist.value.id,
      title: artist.value.name,
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

function goToRelease(releaseId: string) {
  router.push(`/releases/${releaseId}`)
}

onMounted(() => {
  loadArtist()
})
</script>

<template>
  <div class="w-full h-full overflow-y-auto">
    <div v-if="isLoading" class="flex justify-center items-center py-20">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    </div>
    
    <div v-else-if="artist" class="p-6 space-y-6">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-3xl font-bold dark:text-white mb-2">{{ artist.name }}</h1>
          <div v-if="artist.disambiguation" class="text-gray-500 dark:text-gray-400 italic">
            {{ artist.disambiguation }}
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
        <div v-if="artist.type" class="text-sm">
          <span class="font-medium dark:text-gray-300">Type:</span>
          <span class="ml-2 dark:text-gray-400">{{ artist.type }}</span>
        </div>
        <div v-if="artist.country" class="text-sm">
          <span class="font-medium dark:text-gray-300">Country:</span>
          <span class="ml-2 dark:text-gray-400">{{ artist.country }}</span>
        </div>
        <div v-if="artist.life_span" class="text-sm">
          <span class="font-medium dark:text-gray-300">Years:</span>
          <span class="ml-2 dark:text-gray-400">
            {{ artist.life_span.begin || '?' }} - {{ artist.life_span.ended ? (artist.life_span.end || '?') : 'present' }}
          </span>
        </div>
      </div>

      <div v-if="artist.tags && artist.tags.length > 0" class="flex flex-wrap gap-2">
        <span
          v-for="tag in artist.tags"
          :key="tag.name"
          class="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
        >
          {{ tag.name }}
        </span>
      </div>

      <div v-if="artist.releases && artist.releases.length > 0">
        <h2 class="text-2xl font-semibold dark:text-white mb-4">Albums</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="release in artist.releases"
            :key="release.id"
            @click="goToRelease(release.id)"
            class="p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:shadow-md transition-shadow cursor-pointer"
          >
            <h3 class="font-semibold dark:text-white">{{ release.title }}</h3>
            <p v-if="release.date" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {{ release.date }}
            </p>
          </div>
        </div>
      </div>

      <div v-if="artist.recordings && artist.recordings.length > 0">
        <h2 class="text-2xl font-semibold dark:text-white mb-4">Tracks</h2>
        <div class="space-y-2">
          <div
            v-for="recording in artist.recordings"
            :key="recording.id"
            class="p-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"
          >
            <div class="flex justify-between items-center">
              <span class="dark:text-white">{{ recording.title }}</span>
              <span v-if="recording.length" class="text-sm text-gray-500 dark:text-gray-400">
                {{ formatDuration(recording.length) }}
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
