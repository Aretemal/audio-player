import apiClient from '../client'
import type { SearchResult, SearchCategory } from '../types/search'

export type GlobalSearchCategory = 'songs' | 'albums' | 'artists'

export type GlobalSearchItem = {
  id: string | number
  item_type: 'song' | 'album' | 'artist'
  is_saved: boolean
  title?: string
  name?: string
  artist?: string
  album?: string
  src?: string
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

  searchGlobal: (query: string, category: GlobalSearchCategory, skip = 0, limit = 25) => {
    return apiClient.get<GlobalSearchResponse>('/search/global', {
      params: { q: query, category, skip, limit },
    })
  },
}

