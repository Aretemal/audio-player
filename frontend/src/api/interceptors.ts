import type { AxiosError, InternalAxiosRequestConfig } from 'axios'
import apiClient from './client'
import { useAuthStore } from '@/stores/auth'

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: unknown) => void
  reject: (error?: unknown) => void
}> = []

const processQueue = (error: AxiosError | null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve()
    }
  })
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (originalRequest?.url?.includes('/auth/refresh') ||
        originalRequest?.url?.includes('/auth/login') ||
        originalRequest?.url?.includes('/auth/register') ||
        originalRequest?.url?.includes('/auth/me')) {
      return Promise.reject(error)
    }

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(() => {
            return apiClient(originalRequest)
          })
          .catch((err) => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        await apiClient.post('/auth/refresh')
        processQueue(null)
        isRefreshing = false
        return apiClient(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError as AxiosError)
        isRefreshing = false

        const authStore = useAuthStore()
        await authStore.logout()

        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }

        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

