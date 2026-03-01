import apiClient from '../client'
import type { Release } from '../types/release'

export const releaseService = {
  getById: (id: string) => {
    return apiClient.get<Release>(`/releases/${id}`)
  },
}
