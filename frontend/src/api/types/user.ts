export interface User {
  id: number
  email: string
  username: string
  is_active: boolean
  is_superuser: boolean
  theme?: string
  created_at: string
  updated_at: string
}

export interface UserUpdate {
  username?: string
  theme?: string
}

export interface UserCreate {
  email: string
  password: string
  username: string
}

export interface UserLogin {
  email: string
  password: string
}

export interface LoginResponse {
  message: string
  user: {
    id: number
    email: string
    username: string
  }
}

