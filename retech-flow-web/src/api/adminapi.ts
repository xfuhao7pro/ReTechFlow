import request from '@/utils/request'

export interface AdminPageParams {
  page?: number
  page_size?: number
  status?: number | string
  role?: number | string
  keyword?: string
}

export default {
  getDashboard() {
    return request<any>({
      url: '/platform-admin/dashboard/',
      method: 'get',
    })
  },
  getGoods(params?: AdminPageParams) {
    return request<any>({
      url: '/platform-admin/goods/',
      method: 'get',
      params,
    })
  },
  updateGoodsStatus(goodsId: string, status: number, auditReason = '') {
    return request<any>({
      url: `/platform-admin/goods/${goodsId}/status/`,
      method: 'post',
      data: { status, audit_reason: auditReason },
    })
  },
  getOrders(params?: AdminPageParams) {
    return request<any>({
      url: '/platform-admin/orders/',
      method: 'get',
      params,
    })
  },
  getIdentityReviews(params?: AdminPageParams) {
    return request<any>({
      url: '/platform-admin/identity/',
      method: 'get',
      params,
    })
  },
  getUsers(params?: AdminPageParams) {
    return request<any>({
      url: '/platform-admin/users/',
      method: 'get',
      params,
    })
  },
  updateUserRole(userId: string, role: number) {
    return request<any>({
      url: `/platform-admin/users/${userId}/role/`,
      method: 'post',
      data: { role },
    })
  },
  updateUserStatus(userId: string, isActive: boolean) {
    return request<any>({
      url: `/platform-admin/users/${userId}/status/`,
      method: 'post',
      data: { is_active: isActive },
    })
  },
  reviewUserIdentity(userId: string, action: 'approve' | 'reject', reason = '') {
    return request<any>({
      url: `/platform-admin/users/${userId}/verify/`,
      method: 'post',
      data: { action, reason },
    })
  },
  resetUserPassword(userId: string, password: string) {
    return request<any>({
      url: `/platform-admin/users/${userId}/reset-password/`,
      method: 'post',
      data: { password },
    })
  },
  getCategories() {
    return request<any>({
      url: '/platform-admin/categories/',
      method: 'get',
    })
  },
  createCategory(data: { name: string; sort: number }) {
    return request<any>({
      url: '/platform-admin/categories/',
      method: 'post',
      data,
    })
  },
  updateCategory(categoryId: number, data: { name: string; sort: number }) {
    return request<any>({
      url: `/platform-admin/categories/${categoryId}/`,
      method: 'put',
      data,
    })
  },
  deleteCategory(categoryId: number) {
    return request<any>({
      url: `/platform-admin/categories/${categoryId}/`,
      method: 'delete',
    })
  },
  createCategoryAttribute(categoryId: number, data: { name: string; options: string[] }) {
    return request<any>({
      url: `/platform-admin/categories/${categoryId}/attributes/`,
      method: 'post',
      data,
    })
  },
  updateCategoryAttribute(categoryId: number, attrId: number, data: { name: string; options: string[] }) {
    return request<any>({
      url: `/platform-admin/categories/${categoryId}/attributes/${attrId}/`,
      method: 'put',
      data,
    })
  },
  deleteCategoryAttribute(categoryId: number, attrId: number) {
    return request<any>({
      url: `/platform-admin/categories/${categoryId}/attributes/${attrId}/`,
      method: 'delete',
    })
  },
  getAnnouncements(params?: AdminPageParams) {
    return request<any>({
      url: '/platform-admin/announcements/',
      method: 'get',
      params,
    })
  },
  createAnnouncement(data: { title: string; content: string; is_active: boolean }) {
    return request<any>({
      url: '/platform-admin/announcements/',
      method: 'post',
      data,
    })
  },
  updateAnnouncement(noticeId: number, data: { title: string; content: string; is_active: boolean }) {
    return request<any>({
      url: `/platform-admin/announcements/${noticeId}/`,
      method: 'put',
      data,
    })
  },
  deleteAnnouncement(noticeId: number) {
    return request<any>({
      url: `/platform-admin/announcements/${noticeId}/`,
      method: 'delete',
    })
  },
}
