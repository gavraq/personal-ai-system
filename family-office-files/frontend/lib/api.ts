import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from './auth'

// API base URL - in Docker, backend is accessible at this hostname
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // If 401 and we haven't retried yet, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = getRefreshToken()
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token, refresh_token } = response.data
          setTokens(access_token, refresh_token)

          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          // Refresh failed, clear tokens and redirect to login
          clearTokens()
          if (typeof window !== 'undefined') {
            window.location.href = '/login'
          }
          return Promise.reject(refreshError)
        }
      }
    }

    return Promise.reject(error)
  }
)

// Auth API types
export interface RegisterRequest {
  email: string
  password: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UserResponse {
  id: string
  email: string
  role: string
  created_at: string
}

export interface ApiError {
  detail: string
}

// Auth API methods
export const authApi = {
  register: async (data: RegisterRequest): Promise<UserResponse> => {
    const response = await api.post<UserResponse>('/api/auth/register', data)
    return response.data
  },

  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/api/auth/login', data)
    return response.data
  },

  logout: async (refreshToken?: string): Promise<void> => {
    await api.post('/api/auth/logout', refreshToken ? { refresh_token: refreshToken } : {})
  },

  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/api/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  getMe: async (): Promise<UserResponse> => {
    const response = await api.get<UserResponse>('/api/auth/me')
    return response.data
  },
}

// Deal API types
export type DealStatus = 'draft' | 'active' | 'closed'

export interface Deal {
  id: string
  title: string
  description: string | null
  status: DealStatus
  created_by: string
  created_at: string
  updated_at: string | null
}

export interface DealListResponse {
  deals: Deal[]
  total: number
  page: number
  page_size: number
}

export interface DealCreate {
  title: string
  description?: string
}

export interface DealUpdate {
  title?: string
  description?: string
  status?: DealStatus
}

export interface DealMember {
  deal_id: string
  user_id: string
  role_override: string | null
  added_at: string
  user_email: string | null
}

export interface DealMemberListResponse {
  members: DealMember[]
  total: number
}

export interface DealMemberCreate {
  user_id: string
  role_override?: string
}

// Deal API methods
export const dealsApi = {
  list: async (page = 1, pageSize = 20, status?: DealStatus): Promise<DealListResponse> => {
    const params = new URLSearchParams()
    params.append('page', page.toString())
    params.append('page_size', pageSize.toString())
    if (status) {
      params.append('status_filter', status)
    }
    const response = await api.get<DealListResponse>(`/api/deals?${params.toString()}`)
    return response.data
  },

  get: async (dealId: string): Promise<Deal> => {
    const response = await api.get<Deal>(`/api/deals/${dealId}`)
    return response.data
  },

  create: async (data: DealCreate): Promise<Deal> => {
    const response = await api.post<Deal>('/api/deals', data)
    return response.data
  },

  update: async (dealId: string, data: DealUpdate): Promise<Deal> => {
    const response = await api.put<Deal>(`/api/deals/${dealId}`, data)
    return response.data
  },

  delete: async (dealId: string): Promise<void> => {
    await api.delete(`/api/deals/${dealId}`)
  },

  // Deal member methods
  listMembers: async (dealId: string): Promise<DealMemberListResponse> => {
    const response = await api.get<DealMemberListResponse>(`/api/deals/${dealId}/members`)
    return response.data
  },

  addMember: async (dealId: string, data: DealMemberCreate): Promise<DealMember> => {
    const response = await api.post<DealMember>(`/api/deals/${dealId}/members`, data)
    return response.data
  },

  removeMember: async (dealId: string, userId: string): Promise<void> => {
    await api.delete(`/api/deals/${dealId}/members/${userId}`)
  },
}

// File API types
export type FileSource = 'drive' | 'gcs'

export interface DealFile {
  id: string
  deal_id: string
  name: string
  source: FileSource
  source_id: string | null
  mime_type: string | null
  size_bytes: number | null
  uploaded_by: string
  created_at: string
}

export interface FileListResponse {
  files: DealFile[]
  total: number
}

export interface LinkDriveFileRequest {
  drive_file_id: string
  name: string
  mime_type?: string
  size_bytes?: number | null
}

export interface LinkDriveFileResponse {
  id: string
  name: string
  mime_type: string | null
  size_bytes: number | null
  source: string
  source_id: string
}

// File API methods
export const filesApi = {
  list: async (dealId: string, source?: FileSource): Promise<FileListResponse> => {
    const params = new URLSearchParams()
    if (source) {
      params.append('source', source)
    }
    const url = params.toString()
      ? `/api/deals/${dealId}/files?${params.toString()}`
      : `/api/deals/${dealId}/files`
    const response = await api.get<FileListResponse>(url)
    return response.data
  },

  linkDriveFile: async (dealId: string, data: LinkDriveFileRequest): Promise<LinkDriveFileResponse> => {
    const response = await api.post<LinkDriveFileResponse>(`/api/deals/${dealId}/files/link`, data)
    return response.data
  },
}

export default api
