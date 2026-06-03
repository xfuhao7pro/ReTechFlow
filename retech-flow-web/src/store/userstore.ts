import { defineStore } from 'pinia'
import { ref } from 'vue'

// 从 JWT access token 中解码 user_id（兜底方案）
function extractUserIdFromToken(): string | null {
  try {
    const token = localStorage.getItem('access')
    if (!token) return null
    const parts = token.split('.')
    if (parts.length < 2 || !parts[1]) return null
    const payload = JSON.parse(atob(parts[1]))
    return payload.user_id ? String(payload.user_id) : null
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('access') || '')
  // 尝试从 localStorage 恢复用户信息，避免刷新后丢失
  const userName = ref(localStorage.getItem('userName') || '')
  const userAvatar = ref(localStorage.getItem('userAvatar') || '')
  const userRole = ref(Number(localStorage.getItem('userRole') || 0))
  // userId 优先从 localStorage 读取，兜底从 JWT token 解码
  const storedUserId = localStorage.getItem('userId')
  const userId = ref<string | null>(storedUserId || extractUserIdFromToken())
  const isLoggedIn = ref(!!localStorage.getItem('access'))

  // 如果从 JWT 恢复了 userId，同步写回 localStorage 防止下次再走解码
  if (!storedUserId && userId.value) {
    localStorage.setItem('userId', userId.value)
  }

  // 登录后保存 token 和用户信息
  const setLoginState = (
    access: string,
    refresh: string,
    name: string,
    avatar: string = '',
    id: string | null = null,
    role: number = 0,
  ) => {
    token.value = access
    userName.value = name || 'User'
    userAvatar.value = avatar
    userId.value = id
    userRole.value = role
    isLoggedIn.value = true
    
    // 持久化存储
    localStorage.setItem('access', access)
    localStorage.setItem('refresh', refresh)
    localStorage.setItem('userName', userName.value)
    if (avatar) localStorage.setItem('userAvatar', avatar)
    if (id) localStorage.setItem('userId', id)
    if (role) localStorage.setItem('userRole', String(role))
  }

  const setAvatar = (avatarUrl: string) => {
      userAvatar.value = avatarUrl
    }

  // 退出登录
  const logout = () => {
    token.value = ''
    userName.value = ''
    userAvatar.value = ''
    userId.value = null
    userRole.value = 0
    isLoggedIn.value = false
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    localStorage.removeItem('userName')
    localStorage.removeItem('userAvatar')
    localStorage.removeItem('userId')
    localStorage.removeItem('userRole')
  }

  return { 
    token, 
    userName, 
    userAvatar,
    userId,
    userRole,
    isLoggedIn, 
    setLoginState, 
    setAvatar,
    logout 
  }
})
