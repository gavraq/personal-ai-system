import { describe, it, expect, vi } from 'vitest'
import { AxiosError } from 'axios'
import {
  ApiError,
  ErrorCode,
  withRetry,
  getErrorMessage,
  isErrorCode,
} from '@/lib/errors'

describe('ApiError', () => {
  it('creates an error with all properties', () => {
    const error = new ApiError(
      ErrorCode.NOT_FOUND,
      'User not found',
      404,
      { userId: '123' }
    )

    expect(error.code).toBe(ErrorCode.NOT_FOUND)
    expect(error.message).toBe('User not found')
    expect(error.statusCode).toBe(404)
    expect(error.details).toEqual({ userId: '123' })
    expect(error.isTransient).toBe(false)
  })

  it('identifies transient errors', () => {
    const serverError = new ApiError(ErrorCode.INTERNAL_ERROR, 'Server error', 500)
    expect(serverError.isTransient).toBe(true)

    const rateLimited = new ApiError(ErrorCode.RATE_LIMITED, 'Too many requests', 429)
    expect(rateLimited.isTransient).toBe(true)

    const networkError = new ApiError(ErrorCode.NETWORK_ERROR, 'Network error', 0)
    expect(networkError.isTransient).toBe(true)
  })

  it('identifies non-transient errors', () => {
    const notFound = new ApiError(ErrorCode.NOT_FOUND, 'Not found', 404)
    expect(notFound.isTransient).toBe(false)

    const unauthorized = new ApiError(ErrorCode.UNAUTHORIZED, 'Unauthorized', 401)
    expect(unauthorized.isTransient).toBe(false)

    const forbidden = new ApiError(ErrorCode.FORBIDDEN, 'Forbidden', 403)
    expect(forbidden.isTransient).toBe(false)
  })

  it('handles validation errors with field details', () => {
    const validationErrors = [
      { field: 'email', message: 'Invalid email format', type: 'value_error' },
    ]

    const error = new ApiError(
      ErrorCode.VALIDATION_ERROR,
      'Validation failed',
      422,
      { validation_errors: validationErrors },
      validationErrors
    )

    expect(error.validationErrors).toEqual(validationErrors)
    expect(error.getUserMessage()).toBe('email: Invalid email format')
  })

  describe('fromAxiosError', () => {
    it('handles network errors', () => {
      const axiosError = new AxiosError('Network Error')
      const apiError = ApiError.fromAxiosError(axiosError)

      expect(apiError.code).toBe(ErrorCode.NETWORK_ERROR)
      expect(apiError.isTransient).toBe(true)
    })

    it('handles timeout errors', () => {
      const axiosError = new AxiosError('Timeout')
      axiosError.code = 'ECONNABORTED'
      const apiError = ApiError.fromAxiosError(axiosError)

      expect(apiError.code).toBe(ErrorCode.TIMEOUT)
      expect(apiError.isTransient).toBe(true)
    })

    it('handles standard API error responses', () => {
      const axiosError = {
        response: {
          status: 404,
          data: {
            error: 'NOT_FOUND',
            message: 'User not found',
            details: { userId: '123' },
          },
        },
      } as AxiosError<{ error: string; message: string; details: Record<string, unknown> }>

      const apiError = ApiError.fromAxiosError(axiosError)

      expect(apiError.code).toBe('NOT_FOUND')
      expect(apiError.message).toBe('User not found')
      expect(apiError.statusCode).toBe(404)
      expect(apiError.details).toEqual({ userId: '123' })
    })

    it('handles non-standard error responses', () => {
      const axiosError = {
        response: {
          status: 500,
          data: 'Internal Server Error',
        },
      } as unknown as AxiosError

      const apiError = ApiError.fromAxiosError(axiosError)

      expect(apiError.code).toBe(ErrorCode.INTERNAL_ERROR)
      expect(apiError.statusCode).toBe(500)
    })
  })
})

describe('withRetry', () => {
  it('returns result on first success', async () => {
    const fn = vi.fn().mockResolvedValue('success')

    const result = await withRetry(fn)

    expect(result).toBe('success')
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('retries on transient errors', async () => {
    const fn = vi
      .fn()
      .mockRejectedValueOnce(new ApiError(ErrorCode.INTERNAL_ERROR, 'Error', 500))
      .mockResolvedValueOnce('success')

    const result = await withRetry(fn, { baseDelay: 10 })

    expect(result).toBe('success')
    expect(fn).toHaveBeenCalledTimes(2)
  })

  it('does not retry on non-transient errors', async () => {
    const fn = vi
      .fn()
      .mockRejectedValue(new ApiError(ErrorCode.NOT_FOUND, 'Not found', 404))

    await expect(withRetry(fn, { baseDelay: 10 })).rejects.toThrow('Not found')
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('respects max retries', async () => {
    const fn = vi
      .fn()
      .mockRejectedValue(new ApiError(ErrorCode.INTERNAL_ERROR, 'Error', 500))

    await expect(
      withRetry(fn, { maxRetries: 2, baseDelay: 10 })
    ).rejects.toThrow('Error')

    // Initial call + 2 retries = 3 total
    expect(fn).toHaveBeenCalledTimes(3)
  })

  it('uses custom shouldRetry function', async () => {
    const fn = vi
      .fn()
      .mockRejectedValue(new ApiError(ErrorCode.NOT_FOUND, 'Not found', 404))

    // Custom shouldRetry that retries everything
    await expect(
      withRetry(fn, {
        maxRetries: 1,
        baseDelay: 10,
        shouldRetry: () => true,
      })
    ).rejects.toThrow('Not found')

    expect(fn).toHaveBeenCalledTimes(2)
  })
})

describe('getErrorMessage', () => {
  it('returns message from ApiError', () => {
    const error = new ApiError(ErrorCode.NOT_FOUND, 'User not found', 404)
    expect(getErrorMessage(error)).toBe('User not found')
  })

  it('returns validation field message from ApiError', () => {
    const error = new ApiError(
      ErrorCode.VALIDATION_ERROR,
      'Validation failed',
      422,
      {},
      [{ field: 'email', message: 'Invalid format', type: 'value_error' }]
    )
    expect(getErrorMessage(error)).toBe('email: Invalid format')
  })

  it('returns message from standard Error', () => {
    const error = new Error('Standard error')
    expect(getErrorMessage(error)).toBe('Standard error')
  })

  it('returns default message for unknown errors', () => {
    expect(getErrorMessage(null)).toBe('An unexpected error occurred')
    expect(getErrorMessage(undefined)).toBe('An unexpected error occurred')
    expect(getErrorMessage('string error')).toBe('An unexpected error occurred')
  })
})

describe('isErrorCode', () => {
  it('returns true for matching ApiError code', () => {
    const error = new ApiError(ErrorCode.NOT_FOUND, 'Not found', 404)
    expect(isErrorCode(error, ErrorCode.NOT_FOUND)).toBe(true)
  })

  it('returns false for non-matching ApiError code', () => {
    const error = new ApiError(ErrorCode.NOT_FOUND, 'Not found', 404)
    expect(isErrorCode(error, ErrorCode.UNAUTHORIZED)).toBe(false)
  })

  it('handles AxiosError', () => {
    // Create a proper AxiosError instance
    const axiosError = new AxiosError('Not found')
    // @ts-expect-error - setting response property for testing
    axiosError.response = {
      status: 404,
      data: {
        error: 'NOT_FOUND',
        message: 'Not found',
      },
    }

    expect(isErrorCode(axiosError, ErrorCode.NOT_FOUND)).toBe(true)
    expect(isErrorCode(axiosError, ErrorCode.UNAUTHORIZED)).toBe(false)
  })

  it('returns false for non-error values', () => {
    expect(isErrorCode(null, ErrorCode.NOT_FOUND)).toBe(false)
    expect(isErrorCode(undefined, ErrorCode.NOT_FOUND)).toBe(false)
    expect(isErrorCode('string', ErrorCode.NOT_FOUND)).toBe(false)
  })
})
