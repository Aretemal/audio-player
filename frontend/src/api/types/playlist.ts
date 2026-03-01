export type Playlist = {
  id: number
  title: string
  description: string | null
  song_ids: number[] | null
  user_ids: number[] | null
  created_at: string
  updated_at: string
}

export type PlaylistCreate = {
  title: string
  description?: string | null
  song_ids?: number[]
}

export type PlaylistUpdate = {
  title?: string | null
  description?: string | null
  song_ids?: number[] | null
}

