const stripTrailingSlash = (value: string): string => value.replace(/\/+$/, '')

const apiBaseUrl = stripTrailingSlash(
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
)

const inferredWsBaseUrl = apiBaseUrl
  .replace(/^http:/, 'ws:')
  .replace(/^https:/, 'wss:')

export const runtimeConfig = {
  apiBaseUrl,
  wsBaseUrl: stripTrailingSlash(import.meta.env.VITE_WS_BASE_URL || inferredWsBaseUrl)
}

export const buildWsUrl = (path: string, token?: string): string => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  const url = new URL(`${runtimeConfig.wsBaseUrl}${normalizedPath}`)
  if (token) url.searchParams.set('token', token)
  return url.toString()
}
