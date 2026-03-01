import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { useAuthStore } from './auth'
import apiClient from '@/api/client'

export type Theme = 'light' | 'dark'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>('light')
  const authStore = useAuthStore()

  function initTheme() {
    const savedTheme = localStorage.getItem('theme') as Theme | null
    if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
      theme.value = savedTheme
      applyTheme(savedTheme)
    } else if (authStore.user?.theme) {
      theme.value = authStore.user.theme as Theme
      applyTheme(authStore.user.theme as Theme)
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      theme.value = prefersDark ? 'dark' : 'light'
      applyTheme(theme.value)
    }
  }

  function applyTheme(newTheme: Theme) {
    const root = document.documentElement
    if (newTheme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    localStorage.setItem('theme', newTheme)
  }

  async function setTheme(newTheme: Theme) {
    if (newTheme !== 'light' && newTheme !== 'dark') {
      return
    }

    theme.value = newTheme
    applyTheme(newTheme)

    if (authStore.isAuthenticated) {
      try {
        await apiClient.put('/auth/me', { theme: newTheme })
        await authStore.checkAuth()
      } catch (error) {
        console.error('Failed to save theme to profile:', error)
      }
    }
  }

  function toggleTheme() {
    const newTheme = theme.value === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
  }

  watch(
    () => authStore.user?.theme,
    (userTheme) => {
      if (userTheme && userTheme !== theme.value) {
        theme.value = userTheme as Theme
        applyTheme(userTheme as Theme)
      }
    }
  )

  return {
    theme,
    initTheme,
    setTheme,
    toggleTheme,
  }
})

