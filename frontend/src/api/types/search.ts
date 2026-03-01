import type { Song } from './song'
import type { Album } from './album'
import type { Playlist } from './playlist'

export type SearchResult = {
  songs: Song[]
  albums: Album[]
  playlists: Playlist[]
  artists: Array<{
    name: string
    songs_count: number
  }>
}

export type SearchCategory = 'songs' | 'albums' | 'playlists' | 'artists'

