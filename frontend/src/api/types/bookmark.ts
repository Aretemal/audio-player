export type Bookmark = {
  id: number
  user_id: number
  bookmark_type: 'artist' | 'album'
  musicbrainz_id: string
  title: string
  extra_data?: string | null
  categories: BookmarkCategory[]
  created_at: string
  updated_at: string
}

export type BookmarkCategory = {
  id: number
  name: string
  is_default: boolean
  user_id?: number | null
  created_at: string
  updated_at: string
}

export type BookmarkCreate = {
  bookmark_type: 'artist' | 'album'
  musicbrainz_id: string
  title: string
  extra_data?: string | null
  category_ids?: number[]
}

export type BookmarkCategoryCreate = {
  name: string
}
