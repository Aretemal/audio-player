import apiClient from '../client'
import type { SearchResult, SearchCategory } from '../types/search'

export type GlobalSearchCategory = 'songs' | 'albums' | 'artists'

export type SearchProvider = 'musicbrainz' | 'itunes' | 'deezer'

export type GlobalSearchItem = {
  id: string | number
  item_type: 'song' | 'album' | 'artist'
  is_saved?: boolean
  provider?: SearchProvider
  title?: string
  name?: string
  artist?: string
  album?: string
  src?: string
  preview_url?: string | null
  artwork_url?: string | null
  duration_ms?: number | null
  file_size?: number
  created_at?: string
  type?: string
  country?: string
  disambiguation?: string
  date?: string
  status?: string
}

export type GlobalSearchResponse = {
  items: GlobalSearchItem[]
  total: number
  offset: number
  provider?: SearchProvider
}

export const searchService = {
  search: (query: string, categories?: SearchCategory[], skip = 0, limit = 50) => {
    const categoriesParam = categories && categories.length > 0 
      ? categories.join(',') 
      : undefined
    
    const params: Record<string, string | number> = {
      q: query,
      skip,
      limit,
    }
    
    if (categoriesParam) {
      params.categories = categoriesParam
    }
    
    return apiClient.get<SearchResult>('/search', { params })
  },

  searchGlobal: (
    query: string,
    category: GlobalSearchCategory,
    provider: SearchProvider = 'musicbrainz',
    skip = 0,
    limit = 25
  ) => {
    return apiClient.get<GlobalSearchResponse>('/search/global', {
      params: { q: query, category, provider, skip, limit },
    })
  },

  albumDetail: (provider: SearchProvider, albumId: string) => {
    return apiClient.get<{
      id: string
      title?: string
      artist?: string
      artwork_url?: string | null
      provider: SearchProvider
      is_saved: boolean
      bookmark_key: string
      tracks: Array<{
        id: string
        title?: string
        artist?: string | null
        duration_ms?: number | null
        preview_url?: string | null
        track_number?: number | null
      }>
    }>('/search/album-detail', {
      params: { provider, album_id: albumId },
    })
  },
}

