export type Song = {
  id: number
  title: string | null
  artist: string | null
  src: string
  album: string | null
  file_size: number | null
  user_ids: number[]
  created_at: string
  updated_at: string
}

export type SongCreate = {
  title?: string | null
  artist?: string | null
  album?: string | null
  file: File
}

export type SongUpdate = {
  title?: string | null
  artist?: string | null
  album?: string | null
}

