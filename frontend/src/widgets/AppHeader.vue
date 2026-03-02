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
  <nav v-if="isAuthenticated" class="w-full px-10 bg-stone-50 dark:bg-stone-900 flex gap-4 items-center justify-between border-b border-stone-200 dark:border-stone-700">
    <div class="flex gap-4 items-center">
      <RouterLink
        v-for="link in links"
        :key="link.to"
        :to="link.to"
        :class="[
          'p-4 inline-block transition-colors',
          isActive(link.to)
            ? 'text-stone-900 dark:text-stone-100 bg-stone-200 dark:bg-stone-700'
            : 'text-stone-500 dark:text-stone-400 hover:text-stone-700 dark:hover:text-stone-200'
        ]"
      >
        {{ link.label }}
      </RouterLink>
      <div class="flex gap-1 p-1 bg-stone-200 dark:bg-stone-700 rounded-lg ml-2">
        <button
          type="button"
          :class="[
            'px-3 py-1.5 rounded-md text-sm font-medium transition-all cursor-pointer',
            themeStore.theme === 'light'
              ? 'bg-stone-100 dark:bg-stone-600 text-amber-700 dark:text-amber-300 shadow-sm'
              : 'text-stone-500 dark:text-stone-400 hover:text-stone-900 dark:hover:text-stone-200'
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
              ? 'bg-stone-100 dark:bg-stone-600 text-amber-700 dark:text-amber-300 shadow-sm'
              : 'text-stone-500 dark:text-stone-400 hover:text-stone-900 dark:hover:text-stone-200'
          ]"
          title="Dark theme"
          @click="handleThemeChange('dark')"
        >
          🌙
        </button>
      </div>
    </div>
    <div v-if="authStore.isAuthenticated" class="flex items-center gap-4">
      <span class="text-stone-600 dark:text-stone-300">Hello, {{ authStore.user?.username }}!</span>
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
