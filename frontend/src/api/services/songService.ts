import apiClient from '../client'
import type { Song, SongCreate, SongUpdate } from '../types/song'

export const songService = {
  getAll: () => apiClient.get<Song[]>('/songs'),
  getById: (id: number) => apiClient.get<Song>(`/songs/${id}`),
  getByAlbum: (albumId: number) => apiClient.get<Song[]>(`/songs/album/${albumId}`),
  create: (song: SongCreate) => {
    const formData = new FormData()
    formData.append('file', song.file)
    if (song.title) formData.append('title', song.title)
    if (song.artist) formData.append('artist', song.artist)
    if (song.album) formData.append('album', song.album)
    return apiClient.post<Song>('/songs', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  update: (id: number, song: SongUpdate) => apiClient.put<Song>(`/songs/${id}`, song),
  delete: (id: number) => apiClient.delete<void>(`/songs/${id}`),
  getStreamUrl: (id: number) => {
    const baseURL = apiClient.defaults.baseURL || ''
    return `${baseURL}/songs/${id}/stream`
  },
}

