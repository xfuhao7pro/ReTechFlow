import request from '../utils/request'
import type { ApiResponse } from './goodsapi'

export interface CreateSessionData {
  goods_id: string | number
  receiver_id: number
}

export interface ChatMessage {
  id: number | string
  sender: {
    id: string
    nickname: string
    avatar: string
  }
  content: string
  created_at: string
  is_read: boolean
}

export interface ChatSession {
  id: string
  goods: {
    id: number
    title: string
    cover: string
  }
  other_user: {
    id: string
    nickname: string
    avatar: string
  }
  unread_count: number
  last_message: string
  updated_at: string
}

export interface SystemAnnouncement {
  id: number
  title: string
  content: string
  publisher: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// 1. 创建或获取聊天会话
export const createSessionAPI = (data: CreateSessionData) => {
  return request<ApiResponse<{ session_id: string }>>({
    url: '/chats/sessions/',
    method: 'post',
    data
  })
}

// 1.5 获取会话列表
export const getSessionsAPI = () => {
  return request<ApiResponse<ChatSession[]>>({
    url: '/chats/sessions/',
    method: 'get'
  })
}

// 2. 拉取历史消息
export const getMessagesAPI = (sessionId: string) => {
  return request<ApiResponse<ChatMessage[]>>({
    url: `/chats/sessions/${sessionId}/messages/`,
    method: 'get'
  })
}

// 3. 发送消息
export const sendMessageAPI = (data: { session_id: string, content: string }) => {
  return request<ApiResponse<ChatMessage>>({
    url: '/chats/messages/',
    method: 'post',
    data
  })
}

// 4. 标记已读
export const markReadAPI = (sessionId: string) => {
  return request<ApiResponse<any>>({
    url: `/chats/sessions/${sessionId}/read/`,
    method: 'post'
  })
}

export const getSystemAnnouncementsAPI = () => {
  return request<ApiResponse<SystemAnnouncement[]>>({
    url: '/chats/system-announcements/',
    method: 'get'
  })
}

export default {
  createSessionAPI,
  getSessionsAPI,
  getMessagesAPI,
  sendMessageAPI,
  markReadAPI,
  getSystemAnnouncementsAPI
}
