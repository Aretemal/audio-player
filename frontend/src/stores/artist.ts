import { defineStore } from 'pinia'
import { ref } from 'vue'
import { artistService } from '@/api/services/artistService'
import type { Artist, ArtistDetail, ArtistsResponse } from '@/api/types/artist'

export const useArtistStore = defineStore('artist', () => {
  const artists = ref<Artist[]>([])
  const artist = ref<ArtistDetail | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const offset = ref(0)

  async function fetchArtists(query: string = '', limit: number = 25, offsetValue: number = 0) {
    try {
      isLoading.value = true
      error.value = null

      const response = await artistService.getAll({ q: query, limit, offset: offsetValue })
      const data: ArtistsResponse = response.data
      
      artists.value = data.artists
      total.value = data.total
      offset.value = data.offset
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error loading artists'
      artists.value = []
    } finally {
      isLoading.value = false
    }
  }

  async function fetchArtist(id: string) {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await artistService.getById(id)
      artist.value = response.data
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error loading artist'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    artists,
    artist,
    isLoading,
    error,
    total,
    offset,
    fetchArtists,
    fetchArtist,
  }
})
