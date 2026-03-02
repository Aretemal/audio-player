import apiClient from '../client'
import type { Bookmark, BookmarkCategory, BookmarkCreate, BookmarkCategoryCreate } from '../types/bookmark'

export const bookmarkService = {
  getAll: (params?: { bookmark_type?: 'artist' | 'album'; category_id?: number }) => {
    return apiClient.get<Bookmark[]>('/bookmarks', { params })
  },
  getById: (id: number) => {
    return apiClient.get<Bookmark>(`/bookmarks/${id}`)
  },
  create: (bookmark: BookmarkCreate) => {
    return apiClient.post<Bookmark>('/bookmarks', bookmark)
  },
  update: (id: number, bookmark: Partial<BookmarkCreate>) => {
    return apiClient.put<Bookmark>(`/bookmarks/${id}`, bookmark)
  },
  delete: (id: number) => {
    return apiClient.delete(`/bookmarks/${id}`)
  },
  check: (bookmark_type: 'artist' | 'album', musicbrainz_id: string) => {
    return apiClient.get<Bookmark | null>(
      `/bookmarks/check/${bookmark_type}/${encodeURIComponent(musicbrainz_id)}`
    )
  },
  getCategories: () => {
    return apiClient.get<BookmarkCategory[]>('/bookmarks/categories')
  },
  createCategory: (category: BookmarkCategoryCreate) => {
    return apiClient.post<BookmarkCategory>('/bookmarks/categories', category)
  },
}
