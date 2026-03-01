import apiClient from '../client'
import type { Artist, ArtistDetail, ArtistsResponse } from '../types/artist'

export const artistService = {
  getAll: (params?: { q?: string; limit?: number; offset?: number }) => {
    return apiClient.get<ArtistsResponse>('/artists', { params })
  },
  getById: (id: string) => {
    return apiClient.get<ArtistDetail>(`/artists/${id}`)
  },
  getRecordings: (id: string, params?: { limit?: number; offset?: number }) => {
    return apiClient.get(`/artists/${id}/recordings`, { params })
  },
  getReleases: (id: string, params?: { limit?: number; offset?: number }) => {
    return apiClient.get(`/artists/${id}/releases`, { params })
  },
}
