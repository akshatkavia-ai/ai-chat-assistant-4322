import axios from 'axios'

/**
 * Resolve API base URL with dev-friendly autodetection:
 * 1) Use VITE_API_BASE_URL if set
 * 2) Fallback to same host on port 3001 with current protocol
 */
function resolveBaseURL(): string {
  const envUrl = (import.meta as any).env?.VITE_API_BASE_URL
  if (envUrl && typeof envUrl === 'string' && envUrl.trim().length) {
    return envUrl.trim()
  }
  if (typeof window !== 'undefined' && window.location) {
    const { protocol, hostname } = window.location
    return `${protocol}//${hostname}:3001`
  }
  // Final fallback for non-browser contexts
  return 'http://localhost:3001'
}

const BASE_URL = resolveBaseURL()
console.info('[API] Base URL:', BASE_URL)

// PUBLIC_INTERFACE
export const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
  withCredentials: true
})

// PUBLIC_INTERFACE
export async function sendMessage(message: string): Promise<string> {
  try {
    const { data } = await api.post('/chat', { message })
    return data.reply as string
  } catch (error: any) {
    if (error?.response) {
      const status = error.response.status
      const detail = error.response.data?.detail ?? 'Server error'
      throw new Error(`Server error (${status}): ${detail}`)
    }
    if (error?.request) {
      throw new Error(`Cannot connect to backend at ${BASE_URL}. Check network, CORS, or if server is running.`)
    }
    throw new Error(`Unexpected error: ${error?.message ?? String(error)}`)
  }
}

// PUBLIC_INTERFACE
export async function checkHealth(): Promise<any> {
  const { data } = await api.get('/health')
  return data
}
