import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
} from 'axios'
import { ElMessage } from 'element-plus'
import { runtimeConfig } from '@/config/runtime'
import { openAuthDialog } from '@/composables/useAuthDialog'
import { getGuestToken } from '@/utils/guestSession'

interface RetryRequestConfig extends AxiosRequestConfig {
  _retry?: boolean
}

const service: AxiosInstance = axios.create({
  baseURL: runtimeConfig.apiBaseUrl,
  timeout: 10000,
})

let refreshPromise: Promise<string> | null = null

const clearSession = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('userId')
}

const refreshAccessToken = async (): Promise<string> => {
  const refresh = localStorage.getItem('refresh')
  if (!refresh) throw new Error('Missing refresh token')

  if (!refreshPromise) {
    refreshPromise = axios
      .post(`${runtimeConfig.apiBaseUrl}/users/token/refresh/`, { refresh })
      .then((response) => {
        const access = response.data?.access
        if (!access) throw new Error('Missing access token')
        localStorage.setItem('access', access)
        return access
      })
      .finally(() => {
        refreshPromise = null
      })
  }

  return refreshPromise
}

service.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  config.headers['X-Guest-Token'] = getGuestToken()
  return config
})

service.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  async (error) => {
    const status = error.response?.status
    const originalRequest = error.config as RetryRequestConfig | undefined

    if (status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const access = await refreshAccessToken()
        originalRequest.headers = originalRequest.headers || {}
        originalRequest.headers.Authorization = `Bearer ${access}`
        return service(originalRequest)
      } catch {
        clearSession()
        ElMessage.error('登录状态已过期，请重新登录')
        openAuthDialog('login')
        return Promise.reject(error)
      }
    }

    if (status === 400) ElMessage.error(error.response.data.msg || '请求参数错误')
    else if (status === 403) ElMessage.error(error.response.data.msg || '没有权限执行该操作')
    else if (status === 404) ElMessage.error(error.response.data.msg || '请求的资源不存在')
    else if (status) ElMessage.error(error.response.data.msg || '网络请求错误')
    else if (!axios.isCancel(error)) ElMessage.error('网络连接失败')

    return Promise.reject(error)
  },
)

const request = <T>(config: AxiosRequestConfig): Promise<T> => {
  return service(config) as unknown as Promise<T>
}

export default request
