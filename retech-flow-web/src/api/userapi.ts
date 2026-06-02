import request from '../utils/request'

// 定义通用的响应结构接口
export interface ApiResponse<T = any> {
  code: number
  msg: string
  data: T
}

// 定义用户信息的接口
export interface UserProfile {
  id: string
  email: string
  nickname: string
  avatar: string
  bio: string
  gender: number
  location: string | null
  telephone: string | null
  date_joined: string
  is_verified: boolean
}

// 账号与安全数据
export interface SecurityData {
  email: string
  telephone: string
  real_name: string
  id_card: string
  is_verified: boolean
}

// 钱包数据
export interface WalletData {
  balance: string
}

// 获取个人信息接口
const getUserProfileAPI = () => {
  return request<ApiResponse<UserProfile>>({
    url: '/users/profile/',
    method: 'get'
  })
}

// 更新个人信息接口
const updateUserProfileAPI = (data: Partial<UserProfile>) => {
  return request<ApiResponse<UserProfile>>({
    url: '/users/profile/',
    method: 'put',
    data: data
  })
}

// 头像上传接口返回的数据结构
export interface AvatarUploadData {
  url: string
}

// 上传头像接口
const uploadAvatarAPI = (formData: FormData) => {
  return request<ApiResponse<AvatarUploadData>>({
    url: '/users/avatar/upload/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// ================== 地址管理接口 ==================
export interface AddressData {
  id?: number
  receiver_name: string
  telephone: string
  province: string
  city: string
  district: string
  detail_address: string
  is_default: boolean
  is_default_return: boolean
}

// 获取地址列表
const getAddressListAPI = () => {
  return request<ApiResponse<AddressData[]>>({
    url: '/users/addresses/',
    method: 'get'
  })
}

// 新增地址
const addAddressAPI = (data: AddressData) => {
  return request<ApiResponse<AddressData>>({
    url: '/users/addresses/',
    method: 'post',
    data: data
  })
}

// 修改地址
const updateAddressAPI = (id: number, data: Partial<AddressData>) => {
  return request<ApiResponse<AddressData>>({
    url: `/users/addresses/${id}/`,
    method: 'put',
    data: data
  })
}

// ================== 账号安全与资产 ==================
const getSecurityAPI = () => {
  return request<ApiResponse<SecurityData>>({
    url: '/users/security/',
    method: 'get'
  })
}

const updatePhoneAPI = (data: { phone: string; password?: string }) => {
  return request<ApiResponse<any>>({
    url: '/users/user/change-phone/',
    method: 'post',
    data
  })
}

const verifyRealNameAPI = (data: { real_name: string; id_card: string }) => {
  return request<ApiResponse<any>>({
    url: '/users/security/realname/',
    method: 'post',
    data
  })
}

const getWalletAPI = () => {
  return request<ApiResponse<WalletData>>({
    url: '/users/wallet/',
    method: 'get'
  })
}

// 钱包充值接口
const rechargeWalletAPI = (amount: number) => {
  return request<ApiResponse<WalletData>>({
    url: '/users/wallet/recharge/',
    method: 'post',
    data: { amount }
  })
}

export default {
  getUserProfileAPI,
  updateUserProfileAPI,
  uploadAvatarAPI,
  getAddressListAPI,
  addAddressAPI,
  updateAddressAPI,
  getSecurityAPI,
  updatePhoneAPI,
  verifyRealNameAPI,
  getWalletAPI,
  rechargeWalletAPI
}
