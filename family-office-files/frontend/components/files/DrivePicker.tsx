'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { filesApi } from '@/lib/api'

// Declare Google Picker types
declare global {
  interface Window {
    google?: {
      accounts: {
        oauth2: {
          initTokenClient: (config: {
            client_id: string
            scope: string
            callback: (response: { access_token?: string; error?: string }) => void
          }) => {
            requestAccessToken: () => void
          }
        }
      }
      picker?: {
        PickerBuilder: new () => GooglePickerBuilder
        ViewId: {
          DOCS: string
          FOLDERS: string
          SPREADSHEETS: string
          PRESENTATIONS: string
          PDFS: string
        }
        Action: {
          PICKED: string
          CANCEL: string
        }
        Feature: {
          NAV_HIDDEN: string
          MULTISELECT_ENABLED: string
        }
        DocsView: new () => GoogleDocsView
      }
    }
    gapi?: {
      load: (api: string, callback: () => void) => void
      client: {
        init: (config: object) => Promise<void>
        getToken: () => { access_token: string } | null
      }
    }
  }
}

interface GooglePickerBuilder {
  addView: (view: GoogleDocsView | string) => GooglePickerBuilder
  setOAuthToken: (token: string) => GooglePickerBuilder
  setDeveloperKey: (key: string) => GooglePickerBuilder
  setCallback: (callback: (data: GooglePickerResponse) => void) => GooglePickerBuilder
  enableFeature: (feature: string) => GooglePickerBuilder
  setTitle: (title: string) => GooglePickerBuilder
  build: () => { setVisible: (visible: boolean) => void }
}

interface GoogleDocsView {
  setIncludeFolders: (include: boolean) => GoogleDocsView
  setSelectFolderEnabled: (enabled: boolean) => GoogleDocsView
  setMimeTypes: (mimeTypes: string) => GoogleDocsView
}

interface GooglePickerDocument {
  id: string
  name: string
  mimeType: string
  sizeBytes?: number
  url?: string
  iconUrl?: string
  lastEditedUtc?: number
}

interface GooglePickerResponse {
  action: string
  docs?: GooglePickerDocument[]
}

interface DrivePickerProps {
  dealId: string
  onFilesLinked?: (files: LinkedFile[]) => void
  disabled?: boolean
}

export interface LinkedFile {
  id: string
  name: string
  mime_type: string
  size_bytes: number | null
  source: 'drive'
  source_id: string
}

// Google API configuration from environment
const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ''
const GOOGLE_API_KEY = process.env.NEXT_PUBLIC_GOOGLE_API_KEY || ''
const PICKER_SCOPES = 'https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/drive.file'

export function DrivePicker({ dealId, onFilesLinked, disabled }: DrivePickerProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [isGapiLoaded, setIsGapiLoaded] = useState(false)
  const [isPickerLoaded, setIsPickerLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(null)

  // Load Google API scripts
  useEffect(() => {
    // Check if scripts are already loaded
    if (window.gapi && window.google?.picker) {
      setIsGapiLoaded(true)
      setIsPickerLoaded(true)
      return
    }

    // Load GAPI script
    const loadGapi = () => {
      return new Promise<void>((resolve, reject) => {
        if (window.gapi) {
          resolve()
          return
        }

        const script = document.createElement('script')
        script.src = 'https://apis.google.com/js/api.js'
        script.onload = () => {
          window.gapi?.load('client:picker', () => {
            setIsGapiLoaded(true)
            resolve()
          })
        }
        script.onerror = () => reject(new Error('Failed to load Google API'))
        document.body.appendChild(script)
      })
    }

    // Load GSI (Google Sign-In) script
    const loadGsi = () => {
      return new Promise<void>((resolve, reject) => {
        if (window.google?.accounts) {
          resolve()
          return
        }

        const script = document.createElement('script')
        script.src = 'https://accounts.google.com/gsi/client'
        script.onload = () => {
          setIsPickerLoaded(true)
          resolve()
        }
        script.onerror = () => reject(new Error('Failed to load Google Sign-In'))
        document.body.appendChild(script)
      })
    }

    Promise.all([loadGapi(), loadGsi()]).catch((err) => {
      setError(err.message)
    })
  }, [])

  // Create and show the picker
  const showPicker = useCallback((token: string) => {
    if (!window.google?.picker) {
      setError('Google Picker not loaded')
      return
    }

    const view = new window.google.picker.DocsView()
    view.setIncludeFolders(true)
    view.setSelectFolderEnabled(false)

    const picker = new window.google.picker.PickerBuilder()
      .addView(view)
      .setOAuthToken(token)
      .setDeveloperKey(GOOGLE_API_KEY)
      .setCallback(async (data: GooglePickerResponse) => {
        if (data.action === window.google?.picker?.Action.PICKED && data.docs) {
          setIsLoading(true)
          setError(null)

          try {
            // Link each selected file to the deal
            const linkedFiles: LinkedFile[] = []

            for (const doc of data.docs) {
              const linkedFile = await filesApi.linkDriveFile(dealId, {
                drive_file_id: doc.id,
                name: doc.name,
                mime_type: doc.mimeType,
                size_bytes: doc.sizeBytes || null,
              })
              linkedFiles.push(linkedFile)
            }

            onFilesLinked?.(linkedFiles)
          } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } }
            setError(error.response?.data?.detail || 'Failed to link files')
          } finally {
            setIsLoading(false)
          }
        } else if (data.action === window.google?.picker?.Action.CANCEL) {
          // User cancelled - no action needed
        }
      })
      .enableFeature(window.google.picker.Feature.MULTISELECT_ENABLED)
      .setTitle('Select files from Google Drive')
      .build()

    picker.setVisible(true)
  }, [dealId, onFilesLinked])

  // Request access token and show picker
  const handleOpenPicker = useCallback(() => {
    if (!GOOGLE_CLIENT_ID) {
      setError('Google Client ID not configured')
      return
    }

    if (!isGapiLoaded || !isPickerLoaded) {
      setError('Google APIs still loading')
      return
    }

    // If we already have a token, use it
    if (accessToken) {
      showPicker(accessToken)
      return
    }

    // Otherwise, request a new token
    const tokenClient = window.google?.accounts.oauth2.initTokenClient({
      client_id: GOOGLE_CLIENT_ID,
      scope: PICKER_SCOPES,
      callback: (response) => {
        if (response.error) {
          setError('Failed to authenticate with Google')
          return
        }
        if (response.access_token) {
          setAccessToken(response.access_token)
          showPicker(response.access_token)
        }
      },
    })

    tokenClient?.requestAccessToken()
  }, [isGapiLoaded, isPickerLoaded, accessToken, showPicker])

  const isReady = isGapiLoaded && isPickerLoaded && GOOGLE_CLIENT_ID && GOOGLE_API_KEY

  return (
    <div className="space-y-2">
      <Button
        onClick={handleOpenPicker}
        disabled={disabled || isLoading || !isReady}
        variant="outline"
        className="w-full"
      >
        {isLoading ? (
          'Linking files...'
        ) : !isReady ? (
          'Loading Google Drive...'
        ) : (
          <>
            <svg
              className="w-4 h-4 mr-2"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path d="M4.433 22.396l4-6.928H24l-4 6.928H4.433zM15.653 15.468l-4-6.928 4-6.929 4 6.929-4 6.928zM1.545 15.468L5.545 8.54l4 6.928H1.545z" />
            </svg>
            Link from Google Drive
          </>
        )}
      </Button>

      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}
    </div>
  )
}

export default DrivePicker
