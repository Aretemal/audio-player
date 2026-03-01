<script setup lang="ts">
import { AppRoutes } from '@/constants/appRoutes'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { computed } from 'vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

const links = [
  { to: AppRoutes.HOME, label: 'Search' },
  { to: AppRoutes.SONGS, label: 'Songs' },
  { to: AppRoutes.ALBUMS, label: 'Albums' },
  { to: AppRoutes.PLAYLISTS, label: 'Playlists' },
  { to: AppRoutes.ARTISTS, label: 'Artists' },
]

const isActive = (to: string) => {
  if (to === AppRoutes.HOME) return route.path === '/'
  return route.path === to || (to === AppRoutes.ARTISTS && route.path.startsWith('/artists/')) || (to === AppRoutes.ALBUMS && route.path.startsWith('/releases/'))
}

function handleThemeChange(theme: 'light' | 'dark') {
  themeStore.setTheme(theme)
}

async function handleLogout() {
  await authStore.logout()
  router.push(AppRoutes.LOGIN)
}
</script>

<template>
  <nav v-if="isAuthenticated" class="w-full px-10 bg-white dark:bg-gray-800 flex gap-4 items-center justify-between border-b border-gray-200 dark:border-gray-700">
    <div class="flex gap-4 items-center">
      <RouterLink
        v-for="link in links"
        :key="link.to"
        :to="link.to"
        :class="[
          'p-4 inline-block transition-colors',
          isActive(link.to)
            ? 'text-black dark:text-white bg-gray-100 dark:bg-gray-700'
            : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
        ]"
      >
        {{ link.label }}
      </RouterLink>
      <div class="flex gap-1 p-1 bg-gray-100 dark:bg-gray-700 rounded-lg ml-2">
        <button
          type="button"
          :class="[
            'px-3 py-1.5 rounded-md text-sm font-medium transition-all cursor-pointer',
            themeStore.theme === 'light'
              ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          ]"
          title="Light theme"
          @click="handleThemeChange('light')"
        >
          ☀️
        </button>
        <button
          type="button"
          :class="[
            'px-3 py-1.5 rounded-md text-sm font-medium transition-all cursor-pointer',
            themeStore.theme === 'dark'
              ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          ]"
          title="Dark theme"
          @click="handleThemeChange('dark')"
        >
          🌙
        </button>
      </div>
    </div>
    <div v-if="authStore.isAuthenticated" class="flex items-center gap-4">
      <span class="text-gray-600 dark:text-gray-300">Hello, {{ authStore.user?.username }}!</span>
      <el-button type="danger" size="small" @click="handleLogout">
        Logout
      </el-button>
    </div>
    <div v-else>
      <RouterLink :to="AppRoutes.LOGIN">
        <el-button type="primary" size="small">Login</el-button>
      </RouterLink>
    </div>
  </nav>
</template>

<style scoped>
</style>
