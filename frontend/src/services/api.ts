import { ComparisonReport } from '../types'

export interface HealthInfo {
  status: string
  service: string
  model: string
}

/**
 * Send comparison request to backend API.
 */
export async function compareOffers(
  originalFile: File,
  revisedFile: File,
  provider: string = 'auto'
): Promise<ComparisonReport> {
  const formData = new FormData()
  formData.append('original_file', originalFile)
  formData.append('revised_file', revisedFile)

  const url = `/api/compare?provider=${encodeURIComponent(provider)}`
  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`
    try {
      const errorJson = await response.json()
      if (errorJson.detail) {
        errorDetail = typeof errorJson.detail === 'string' 
          ? errorJson.detail 
          : JSON.stringify(errorJson.detail)
      }
    } catch {
      // Use fallback errorDetail
    }
    throw new Error(errorDetail)
  }

  return response.json()
}

/**
 * Fetch a sample PDF from public/samples/ as a File object.
 */
export async function fetchSampleFile(filename: string): Promise<File> {
  const response = await fetch(`/samples/${filename}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch sample file: ${filename} (HTTP ${response.status})`)
  }
  const blob = await response.blob()
  return new File([blob], filename, { type: 'application/pdf' })
}

/**
 * Check backend health and model configuration.
 */
export async function checkBackendHealth(): Promise<HealthInfo> {
  const response = await fetch('/health')
  if (!response.ok) {
    throw new Error(`Backend health check failed: HTTP ${response.status}`)
  }
  return response.json()
}
