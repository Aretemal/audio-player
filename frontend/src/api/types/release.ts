export type Release = {
  id: string
  title: string
  artists?: Array<{
    id: string
    name: string
  }>
  date?: string | null
  country?: string | null
  barcode?: string | null
  status?: string | null
  tracks?: Array<{
    id: string
    title: string
    length?: number | null
    position?: number | null
  }>
}
