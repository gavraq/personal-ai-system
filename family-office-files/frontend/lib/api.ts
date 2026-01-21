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
  file_count: number
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

export interface UploadFileResponse {
  id: string
  name: string
  mime_type: string | null
  size_bytes: number
  source: 'gcs'
  source_id: string
}

export interface FileDownloadResponse {
  id: string
  name: string
  download_url: string
  expires_in_minutes: number
}

export type FilePermission = 'view' | 'edit'

export interface ShareFileRequest {
  user_id: string
  permission: FilePermission
}

export interface FileShareInfo {
  file_id: string
  shared_with: string
  permission: FilePermission
  shared_at: string
}

export interface ShareFileResponse {
  message: string
  share: FileShareInfo
}

// File list options
export type FileSortBy = 'name' | 'date' | 'type'
export type SortOrder = 'asc' | 'desc'

export interface FileListOptions {
  source?: FileSource
  search?: string
  sortBy?: FileSortBy
  sortOrder?: SortOrder
}

// File API methods
export const filesApi = {
  list: async (dealId: string, options?: FileListOptions): Promise<FileListResponse> => {
    const params = new URLSearchParams()
    if (options?.source) {
      params.append('source', options.source)
    }
    if (options?.search) {
      params.append('search', options.search)
    }
    if (options?.sortBy) {
      params.append('sort_by', options.sortBy)
    }
    if (options?.sortOrder) {
      params.append('sort_order', options.sortOrder)
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

  getDownloadUrl: async (fileId: string): Promise<FileDownloadResponse> => {
    const response = await api.get<FileDownloadResponse>(`/api/files/${fileId}/download`)
    return response.data
  },

  delete: async (fileId: string): Promise<void> => {
    await api.delete(`/api/files/${fileId}`)
  },

  share: async (fileId: string, data: ShareFileRequest): Promise<ShareFileResponse> => {
    const response = await api.post<ShareFileResponse>(`/api/files/${fileId}/share`, data)
    return response.data
  },
}

// Activity API types
export type ActivityType = 'file_upload' | 'file_link' | 'file_delete' | 'deal_create' | 'deal_update' | 'deal_delete' | 'member_add' | 'member_remove' | 'agent_run'

export interface Activity {
  id: string
  deal_id: string
  actor_id: string
  actor_email: string | null
  action: ActivityType
  details: Record<string, unknown> | null
  created_at: string
}

export interface ActivityListResponse {
  activities: Activity[]
  total: number
  page: number
  page_size: number
}

export interface ActivityListOptions {
  page?: number
  pageSize?: number
  dealId?: string
  action?: ActivityType
}

// Activity API methods
export const activityApi = {
  list: async (options?: ActivityListOptions): Promise<ActivityListResponse> => {
    const params = new URLSearchParams()
    if (options?.page) {
      params.append('page', options.page.toString())
    }
    if (options?.pageSize) {
      params.append('page_size', options.pageSize.toString())
    }
    if (options?.dealId) {
      params.append('deal_id', options.dealId)
    }
    if (options?.action) {
      params.append('action', options.action)
    }
    const url = params.toString()
      ? `/api/activity?${params.toString()}`
      : '/api/activity'
    const response = await api.get<ActivityListResponse>(url)
    return response.data
  },

  listForDeal: async (dealId: string, page = 1, pageSize = 20): Promise<ActivityListResponse> => {
    const params = new URLSearchParams()
    params.append('page', page.toString())
    params.append('page_size', pageSize.toString())
    const response = await api.get<ActivityListResponse>(`/api/activity/deal/${dealId}?${params.toString()}`)
    return response.data
  },
}

// Agent API types
export type AgentType = 'market_research' | 'document_analysis' | 'due_diligence' | 'news_alerts'
export type AgentStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface AgentRun {
  id: string
  deal_id: string
  user_id: string
  user_email: string | null
  agent_type: AgentType
  status: AgentStatus
  input: Record<string, unknown>
  output: Record<string, unknown> | null
  error_message: string | null
  started_at: string
  completed_at: string | null
}

export interface AgentRunListResponse {
  runs: AgentRun[]
  total: number
  page: number
  page_size: number
}

export interface AgentSummary {
  id: string
  deal_id: string
  deal_title: string
  agent_type: AgentType
  status: AgentStatus
  summary_excerpt: string | null
  started_at: string
  completed_at: string | null
}

export interface AgentSummaryListResponse {
  summaries: AgentSummary[]
  total: number
}

export interface AgentListOptions {
  page?: number
  pageSize?: number
  dealId?: string
  agentType?: AgentType
  status?: AgentStatus
}

export interface AgentMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
}

export interface AgentMessagesResponse {
  messages: AgentMessage[]
  total: number
}

export interface AgentRunStartRequest {
  query?: string
  file_id?: string
  context?: Record<string, unknown>
}

export interface AgentRunStartResponse {
  run_id: string
  status: AgentStatus
  message: string
}

// Agent API methods
export const agentsApi = {
  listRuns: async (options?: AgentListOptions): Promise<AgentRunListResponse> => {
    const params = new URLSearchParams()
    if (options?.page) {
      params.append('page', options.page.toString())
    }
    if (options?.pageSize) {
      params.append('page_size', options.pageSize.toString())
    }
    if (options?.dealId) {
      params.append('deal_id', options.dealId)
    }
    if (options?.agentType) {
      params.append('agent_type', options.agentType)
    }
    if (options?.status) {
      params.append('status_filter', options.status)
    }
    const url = params.toString()
      ? `/api/agents/runs?${params.toString()}`
      : '/api/agents/runs'
    const response = await api.get<AgentRunListResponse>(url)
    return response.data
  },

  getRun: async (runId: string): Promise<AgentRun> => {
    const response = await api.get<AgentRun>(`/api/agents/runs/${runId}`)
    return response.data
  },

  listSummaries: async (limit = 10): Promise<AgentSummaryListResponse> => {
    const response = await api.get<AgentSummaryListResponse>(`/api/agents/summaries?limit=${limit}`)
    return response.data
  },

  listDealRuns: async (dealId: string, page = 1, pageSize = 20, agentType?: AgentType): Promise<AgentRunListResponse> => {
    const params = new URLSearchParams()
    params.append('page', page.toString())
    params.append('page_size', pageSize.toString())
    if (agentType) {
      params.append('agent_type', agentType)
    }
    const response = await api.get<AgentRunListResponse>(`/api/agents/deal/${dealId}/runs?${params.toString()}`)
    return response.data
  },

  startRun: async (agentType: AgentType, dealId: string, request: AgentRunStartRequest): Promise<AgentRunStartResponse> => {
    const params = new URLSearchParams()
    params.append('deal_id', dealId)
    const response = await api.post<AgentRunStartResponse>(`/api/agents/${agentType}/run?${params.toString()}`, request)
    return response.data
  },

  getMessages: async (runId: string): Promise<AgentMessagesResponse> => {
    const response = await api.get<AgentMessagesResponse>(`/api/agents/runs/${runId}/messages`)
    return response.data
  },
}

export default api
