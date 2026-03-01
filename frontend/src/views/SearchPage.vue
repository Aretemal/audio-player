<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Loading, Plus, Check } from '@element-plus/icons-vue'
import { searchService, type GlobalSearchCategory, type GlobalSearchItem } from '@/api/services/searchService'
import { bookmarkService } from '@/api/services/bookmarkService'
import { useSongStore } from '@/stores/song'
import { ElMessage } from 'element-plus'
import { AppRoutes } from '@/constants/appRoutes'

const router = useRouter()
const songStore = useSongStore()

const activeTab = ref<GlobalSearchCategory>('songs')
const query = ref('')
const isLoading = ref(false)
const items = ref<GlobalSearchItem[]>([])
const total = ref(0)
const offset = ref(0)
const limit = 25

async function runSearch() {
  if (!query.value.trim()) {
    items.value = []
    total.value = 0
    return
  }
  isLoading.value = true
  try {
    const res = await searchService.searchGlobal(
      query.value.trim(),
      activeTab.value,
      offset.value,
      limit
    )
    items.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    console.error(e)
    items.value = []
    total.value = 0
  } finally {
    isLoading.value = false
  }
}

function getStreamUrl(songId: number): string {
  return songStore.getStreamUrl(songId)
}

async function toggleSave(item: GlobalSearchItem) {
  if (item.item_type === 'song') return
  if (item.is_saved) {
    try {
      const check = await bookmarkService.check(
        item.item_type as 'artist' | 'album',
        String(item.id)
      )
      if (check.data?.id) {
        await bookmarkService.delete(check.data.id)
        item.is_saved = false
        ElMessage.success('Removed from saved')
      }
    } catch (e) {
      ElMessage.error('Error removing bookmark')
    }
    return
  }
  try {
    const title = item.item_type === 'artist' ? item.name : item.title
    await bookmarkService.create({
      bookmark_type: item.item_type as 'artist' | 'album',
      musicbrainz_id: String(item.id),
      title: title || '',
    })
    item.is_saved = true
    ElMessage.success('Added to saved')
  } catch (e) {
    ElMessage.error('Error saving')
  }
}

function goToArtist(id: string) {
  router.push(`/artists/${id}`)
}

function goToRelease(id: string) {
  router.push(`/releases/${id}`)
}

const tabs = [
  { value: 'songs' as GlobalSearchCategory, label: 'Songs' },
  { value: 'albums' as GlobalSearchCategory, label: 'Albums' },
  { value: 'artists' as GlobalSearchCategory, label: 'Artists' },
]

watch([activeTab, query], () => {
  offset.value = 0
  runSearch()
})
</script>

<template>
  <div class="w-full h-full flex flex-col gap-4">
    <h1 class="text-2xl font-bold dark:text-white">Search</h1>

    <div class="flex gap-2 items-center flex-wrap">
      <div class="relative flex-1 min-w-[200px] max-w-md">
        <el-input
          v-model="query"
          placeholder="Songs, albums, artists..."
          clearable
          class="w-full"
          @keyup.enter="runSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <el-button type="primary" :loading="isLoading" @click="runSearch">
        Search
      </el-button>
    </div>

    <div class="flex gap-2 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg">
      <button
        v-for="t in tabs"
        :key="t.value"
        :class="[
          'px-4 py-2 rounded-md font-medium transition-all cursor-pointer',
          activeTab === t.value
            ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
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
      <div v-else-if="!query.trim()" class="text-center py-12 text-gray-500 dark:text-gray-400">
        Enter a query and click Search
      </div>
      <div v-else-if="items.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No results found
      </div>
      <div v-else class="flex flex-col gap-3">
        <template v-if="activeTab === 'songs'">
          <div
            v-for="item in items"
            :key="item.id"
            class="p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"
          >
            <div class="flex flex-col gap-2">
              <div class="flex justify-between items-start">
                <div>
                  <h3 class="font-semibold text-lg dark:text-white">{{ item.title || 'Untitled' }}</h3>
                  <p class="text-sm text-gray-600 dark:text-gray-300">{{ item.artist || '—' }}</p>
                  <p v-if="item.album" class="text-xs text-gray-500 dark:text-gray-400">{{ item.album }}</p>
                </div>
              </div>
              <audio
                v-if="item.id != null"
                :src="getStreamUrl(Number(item.id))"
                controls
                class="w-full max-w-md"
              />
            </div>
          </div>
        </template>

        <template v-else-if="activeTab === 'albums'">
          <div
            v-for="item in items"
            :key="item.id"
            class="p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex justify-between items-center"
          >
            <div
              class="cursor-pointer flex-1 min-w-0"
              @click="goToRelease(String(item.id))"
            >
              <h3 class="font-semibold text-lg dark:text-white">{{ item.title || 'Untitled' }}</h3>
              <p class="text-sm text-gray-600 dark:text-gray-300">{{ item.artist || '—' }}</p>
              <p v-if="item.date" class="text-xs text-gray-500 dark:text-gray-400">{{ item.date }}</p>
            </div>
            <el-button
              :type="item.is_saved ? 'success' : 'primary'"
              size="small"
              @click="toggleSave(item)"
            >
              <el-icon v-if="item.is_saved"><Check /></el-icon>
              <el-icon v-else><Plus /></el-icon>
              <span class="ml-1">{{ item.is_saved ? 'Saved' : 'Save' }}</span>
            </el-button>
          </div>
        </template>

        <template v-else-if="activeTab === 'artists'">
          <div
            v-for="item in items"
            :key="item.id"
            class="p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex justify-between items-center"
          >
            <div
              class="cursor-pointer flex-1 min-w-0"
              @click="goToArtist(String(item.id))"
            >
              <h3 class="font-semibold text-lg dark:text-white">{{ item.name || '—' }}</h3>
              <p v-if="item.country" class="text-sm text-gray-600 dark:text-gray-300">{{ item.country }}</p>
              <p v-if="item.disambiguation" class="text-xs text-gray-500 dark:text-gray-400">{{ item.disambiguation }}</p>
            </div>
            <el-button
              :type="item.is_saved ? 'success' : 'primary'"
              size="small"
              @click="toggleSave(item)"
            >
              <el-icon v-if="item.is_saved"><Check /></el-icon>
              <el-icon v-else><Plus /></el-icon>
              <span class="ml-1">{{ item.is_saved ? 'Saved' : 'Save' }}</span>
            </el-button>
          </div>
        </template>
      </div>

      <p v-if="total > limit && items.length" class="text-sm text-gray-500 dark:text-gray-400 mt-2">
        Showing {{ items.length }} of {{ total }}
      </p>
    </div>
  </div>
</template>

<style scoped>
</style>
