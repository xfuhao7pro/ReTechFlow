const GUEST_TOKEN_KEY = 'retechflow_guest_token'
const GUEST_VALUATION_USED_KEY = 'retechflow_guest_valuation_used'

const createGuestToken = (): string => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID().replace(/-/g, '')
  }
  return `${Date.now()}${Math.random().toString(16).slice(2)}`.padEnd(32, '0').slice(0, 64)
}

export const getGuestToken = (): string => {
  const saved = localStorage.getItem(GUEST_TOKEN_KEY)
  if (saved) return saved

  const token = createGuestToken()
  localStorage.setItem(GUEST_TOKEN_KEY, token)
  return token
}

export const hasUsedGuestValuation = (): boolean => {
  return localStorage.getItem(GUEST_VALUATION_USED_KEY) === '1'
}

export const markGuestValuationUsed = () => {
  localStorage.setItem(GUEST_VALUATION_USED_KEY, '1')
}
