import apiClient from '../client'
import type { Playlist, PlaylistCreate, PlaylistUpdate } from '../types/playlist'

export const playlistService = {
  getAll: () => apiClient.get<Playlist[]>('/playlists'),
  getById: (id: number) => apiClient.get<Playlist>(`/playlists/${id}`),
  create: (playlist: PlaylistCreate) => apiClient.post<Playlist>('/playlists', playlist),
  update: (id: number, playlist: PlaylistUpdate) => apiClient.put<Playlist>(`/playlists/${id}`, playlist),
  delete: (id: number) => apiClient.delete<void>(`/playlists/${id}`),
}

