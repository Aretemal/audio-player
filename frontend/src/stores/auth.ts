import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/client'
import type { User } from '@/api/types/user'
import { ElNotification } from 'element-plus'
import type { AxiosError } from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const isCheckingAuth = ref(false)
  const error = ref<string | null>(null)
  let checkAuthPromise: Promise<boolean> | null = null

  const isAuthenticated = computed(() => !!user.value)

  async function checkAuth(silent = false) {
    if (checkAuthPromise) {
      return checkAuthPromise
    }

    checkAuthPromise = (async () => {
      try {
        isCheckingAuth.value = true
        error.value = null

        const { data } = await apiClient.get('/auth/me')

        user.value = data

        return true
      } catch (err) {
        const axiosError = err as AxiosError<{ detail?: string }>
        const errorCode = axiosError.code
        if (errorCode === 'ECONNABORTED' || axiosError.message === 'Request aborted') {
          return false
        }

        const status = axiosError.response?.status
        if (!silent && status !== 401 && status !== 403) {
          ElNotification({
            message: 'Authentication check failed. Please try again later.',
            type: 'error',
            duration: 3000,
          })
        }

        user.value = null

        return false
      } finally {
        isCheckingAuth.value = false
        checkAuthPromise = null
      }
    })()

    return checkAuthPromise
  }

  async function login(email: string, password: string) {
    try {
      isLoading.value = true
      error.value = null

      const { data } = await apiClient.post('/auth/login', {
        email,
        password,
      })

      user.value = {
        id: data.user.id,
        email: data.user.email,
        username: data.user.username,
        is_active: true,
        is_superuser: false,
        created_at: '',
        updated_at: '',
      }

      await checkAuth()

      return { success: true }
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      const errorMessage = axiosError.response?.data?.detail || 'Login failed'

      error.value = errorMessage

      return {
        success: false,
        error: errorMessage,
      }
    } finally {
      isLoading.value = false
    }
  }

  async function register(email: string, password: string, username: string) {
    try {
      isLoading.value = true
      error.value = null
      const { data } = await apiClient.post('/auth/register', {
        email,
        password,
        username,
      })
      return { success: true, user: data }
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      const errorMessage = axiosError.response?.data?.detail || 'Registration failed'
      error.value = errorMessage
      return {
        success: false,
        error: errorMessage,
      }
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    try {
      await apiClient.post('/auth/logout');
      error.value = null
    } catch {
      ElNotification({
        message: 'Logout failed. Please try again later.',
        type: 'error',
        duration: 3000,
      })
    } finally {
      user.value = null
    }
  }

  return {
    user,
    isLoading,
    isCheckingAuth,
    error,
    isAuthenticated,
    checkAuth,
    login,
    register,
    logout,
  }
})

