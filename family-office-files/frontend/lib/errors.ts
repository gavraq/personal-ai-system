/**
 * API Error handling utilities with retry logic for transient failures.
 *
 * Error Response Format (matches backend):
 * {
 *   error: string;        // Machine-readable error code (e.g., "VALIDATION_ERROR")
 *   message: string;      // Human-readable message
 *   details?: object;     // Optional additional context
 * }
 */

import { AxiosError } from 'axios'

// Error codes matching backend ErrorCode enum
export enum ErrorCode {
  // Authentication errors (401)
  UNAUTHORIZED = 'UNAUTHORIZED',
  INVALID_TOKEN = 'INVALID_TOKEN',
  TOKEN_EXPIRED = 'TOKEN_EXPIRED',

  // Permission errors (403)
  FORBIDDEN = 'FORBIDDEN',
  INSUFFICIENT_PERMISSIONS = 'INSUFFICIENT_PERMISSIONS',

  // Not found errors (404)
  NOT_FOUND = 'NOT_FOUND',
  RESOURCE_NOT_FOUND = 'RESOURCE_NOT_FOUND',

  // Validation errors (400/422)
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  BAD_REQUEST = 'BAD_REQUEST',
  INVALID_INPUT = 'INVALID_INPUT',

  // Conflict errors (409)
  CONFLICT = 'CONFLICT',
  ALREADY_EXISTS = 'ALREADY_EXISTS',

  // Server errors (500)
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR',
  EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR',

  // Rate limiting (429)
  RATE_LIMITED = 'RATE_LIMITED',

  // Network errors (client-side)
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT = 'TIMEOUT',
}

export interface ApiErrorResponse {
  error: string
  message: string
  details?: Record<string, unknown>
}

export interface ValidationError {
  field: string
  message: string
  type: string
}

// Error codes that indicate transient failures worth retrying
const TRANSIENT_ERROR_CODES = new Set([
  ErrorCode.INTERNAL_ERROR,
  ErrorCode.DATABASE_ERROR,
  ErrorCode.EXTERNAL_SERVICE_ERROR,
  ErrorCode.RATE_LIMITED,
  ErrorCode.NETWORK_ERROR,
  ErrorCode.TIMEOUT,
])

// HTTP status codes that indicate transient failures
const TRANSIENT_STATUS_CODES = new Set([408, 429, 500, 502, 503, 504])

export class ApiError extends Error {
  public readonly code: string
  public readonly statusCode: number
  public readonly details?: Record<string, unknown>
  public readonly isTransient: boolean
  public readonly validationErrors?: ValidationError[]

  constructor(
    code: string,
    message: string,
    statusCode: number,
    details?: Record<string, unknown>,
    validationErrors?: ValidationError[]
  ) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.statusCode = statusCode
    this.details = details
    this.validationErrors = validationErrors
    this.isTransient =
      TRANSIENT_ERROR_CODES.has(code as ErrorCode) ||
      TRANSIENT_STATUS_CODES.has(statusCode)
  }

  static fromAxiosError(error: AxiosError<ApiErrorResponse>): ApiError {
    // Network error (no response)
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        return new ApiError(
          ErrorCode.TIMEOUT,
          'Request timed out. Please try again.',
          0
        )
      }
      return new ApiError(
        ErrorCode.NETWORK_ERROR,
        'Network error. Please check your connection.',
        0
      )
    }

    const { status, data } = error.response

    // If we have a standard error response
    if (data && typeof data === 'object' && 'error' in data && 'message' in data) {
      const validationErrors =
        data.details?.validation_errors as ValidationError[] | undefined

      return new ApiError(
        data.error,
        data.message,
        status,
        data.details,
        validationErrors
      )
    }

    // Fallback for non-standard error responses
    const defaultMessages: Record<number, string> = {
      400: 'Invalid request',
      401: 'Authentication required',
      403: 'Access denied',
      404: 'Resource not found',
      409: 'Resource conflict',
      422: 'Validation error',
      429: 'Too many requests. Please wait and try again.',
      500: 'Server error. Please try again later.',
    }

    const defaultCodes: Record<number, ErrorCode> = {
      400: ErrorCode.BAD_REQUEST,
      401: ErrorCode.UNAUTHORIZED,
      403: ErrorCode.FORBIDDEN,
      404: ErrorCode.NOT_FOUND,
      409: ErrorCode.CONFLICT,
      422: ErrorCode.VALIDATION_ERROR,
      429: ErrorCode.RATE_LIMITED,
      500: ErrorCode.INTERNAL_ERROR,
    }

    return new ApiError(
      defaultCodes[status] || ErrorCode.INTERNAL_ERROR,
      defaultMessages[status] || 'An unexpected error occurred',
      status
    )
  }

  // Get user-friendly error message
  getUserMessage(): string {
    // For validation errors, provide more context
    if (this.validationErrors && this.validationErrors.length > 0) {
      const firstError = this.validationErrors[0]
      return `${firstError.field}: ${firstError.message}`
    }

    return this.message
  }
}

// Retry configuration
export interface RetryConfig {
  maxRetries: number
  baseDelay: number // ms
  maxDelay: number // ms
  shouldRetry?: (error: ApiError) => boolean
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  baseDelay: 1000,
  maxDelay: 10000,
  shouldRetry: (error) => error.isTransient,
}

// Calculate delay with exponential backoff and jitter
function calculateRetryDelay(attempt: number, config: RetryConfig): number {
  const exponentialDelay = config.baseDelay * Math.pow(2, attempt)
  const jitter = Math.random() * 0.3 * exponentialDelay // 30% jitter
  const delay = Math.min(exponentialDelay + jitter, config.maxDelay)
  return Math.round(delay)
}

// Sleep utility
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Execute a function with automatic retry for transient failures.
 *
 * @param fn - Async function to execute
 * @param config - Retry configuration (optional)
 * @returns Promise with the function result
 * @throws ApiError if all retries fail
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  config: Partial<RetryConfig> = {}
): Promise<T> {
  const finalConfig = { ...DEFAULT_RETRY_CONFIG, ...config }
  let lastError: ApiError | undefined

  for (let attempt = 0; attempt <= finalConfig.maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      // Convert to ApiError if needed
      const apiError =
        error instanceof ApiError
          ? error
          : error instanceof AxiosError
            ? ApiError.fromAxiosError(error)
            : new ApiError(
                ErrorCode.INTERNAL_ERROR,
                error instanceof Error ? error.message : 'Unknown error',
                500
              )

      lastError = apiError

      // Check if we should retry
      const shouldRetry = finalConfig.shouldRetry?.(apiError) ?? apiError.isTransient
      const hasRetriesLeft = attempt < finalConfig.maxRetries

      if (shouldRetry && hasRetriesLeft) {
        const delay = calculateRetryDelay(attempt, finalConfig)
        console.warn(
          `API request failed (attempt ${attempt + 1}/${finalConfig.maxRetries + 1}), ` +
            `retrying in ${delay}ms...`,
          apiError.code
        )
        await sleep(delay)
        continue
      }

      // No more retries, throw the error
      throw apiError
    }
  }

  // This should never be reached, but TypeScript needs it
  throw lastError || new ApiError(ErrorCode.INTERNAL_ERROR, 'Unknown error', 500)
}

/**
 * Parse an error and return a user-friendly message.
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.getUserMessage()
  }

  if (error instanceof AxiosError) {
    return ApiError.fromAxiosError(error).getUserMessage()
  }

  if (error instanceof Error) {
    return error.message
  }

  return 'An unexpected error occurred'
}

/**
 * Check if an error is a specific type
 */
export function isErrorCode(error: unknown, code: ErrorCode): boolean {
  if (error instanceof ApiError) {
    return error.code === code
  }

  if (error instanceof AxiosError) {
    const apiError = ApiError.fromAxiosError(error)
    return apiError.code === code
  }

  return false
}
