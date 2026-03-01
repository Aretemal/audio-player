export type Artist = {
  id: string
  name: string
  type?: string | null
  country?: string | null
  disambiguation?: string | null
  life_span?: {
    begin?: string | null
    end?: string | null
    ended?: boolean | null
  } | null
  tags?: string[]
}

export type ArtistDetail = {
  id: string
  name: string
  type?: string | null
  country?: string | null
  disambiguation?: string | null
  life_span?: {
    begin?: string | null
    end?: string | null
    ended?: boolean | null
  } | null
  aliases?: string[]
  tags?: Array<{
    name: string
    count: number
  }>
  releases?: Array<{
    id: string
    title: string
    date?: string | null
    status?: string | null
  }>
  recordings?: Array<{
    id: string
    title: string
    length?: number | null
  }>
}

export type ArtistsResponse = {
  artists: Artist[]
  count: number
  total: number
  offset: number
}
