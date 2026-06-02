import request from '../utils/request'

// 定义通用的响应结构接口
export interface ApiResponse<T = any> {
  code: number
  msg: string
  data: T
}


// 登录接口返回的数据结构
export interface LoginData {
  access: string
  refresh: string
  user_info: object
}

// 注册接口参数
export interface RegisterData {
  email: string
  auth_code: string
  password: string
  password_confirm: string
}

// 重置密码接口参数
export interface ResetPasswordData {
  email: string
  auth_code: string
  password: string
  password_confirm: string
}

// 登录接口
const loginAPI = (data: object) => {
  return request<ApiResponse<LoginData>>({
    url: '/users/login/',
    method: 'post',
    data: data
  })
}

// 注册接口
const registerAPI = (data: RegisterData) => {
  return request<ApiResponse<null>>({
    url: '/users/register/',
    method: 'post',
    data: data
  })
}

// 发送验证码接口
const sendCodeAPI = (email: string) => {
  return request<ApiResponse<null>>({
    url: '/users/send-code/',
    method: 'post',
    data: { email }
  })
}

// 重置密码接口
const resetPasswordAPI = (data: ResetPasswordData) => {
  return request<ApiResponse<null>>({
    url: '/users/resetpwd/',
    method: 'post',
    data: data
  })
}

export default {
  loginAPI,
  registerAPI,
  sendCodeAPI,
  resetPasswordAPI
}
