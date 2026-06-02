import request from '@/utils/request'

export interface OrderCreateData {
  goods_id: string
  receiver_name: string
  receiver_phone: string
  receiver_address: string
}

export interface ApiResponse<T = any> {
  code: number
  msg: string
  data: T
}

export default {
  /**
   * 创建订单
   */
  createOrder(data: OrderCreateData) {
    return request<ApiResponse>({
      url: '/orders/create/',
      method: 'post',
      data
    })
  },

  /**
   * 支付订单
   */
  payOrder(orderId: string) {
    return request<ApiResponse>({
      url: `/orders/${orderId}/pay/`,
      method: 'post'
    })
  },

  /**
   * 获取我买到的订单列表
   */
  getMyBoughtOrders(params?: { status?: number | string }) {
    return request<ApiResponse>({
      url: '/orders/my/',
      method: 'get',
      params
    })
  },

  /**
   * 获取我卖出的订单列表
   */
  getMySoldOrders(params?: { status?: number | string }) {
    return request<ApiResponse>({
      url: '/orders/sell/',
      method: 'get',
      params
    })
  },

  /**
   * 订单发货
   */
  shipOrder(orderId: string, data: { delivery_method: number, tracking_number?: string }) {
    return request<ApiResponse>({
      url: `/orders/${orderId}/ship/`,
      method: 'post',
      data
    })
  },

  /**
   * 获取订单物流信息
   */
  getOrderLogistics(orderId: string) {
    return request<ApiResponse>({
      url: `/orders/${orderId}/logistics/`,
      method: 'get'
    })
  },

  /**
   * 确认收货
   */
  confirmReceipt(orderId: string) {
    return request<ApiResponse>({
      url: `/orders/${orderId}/confirm/`,
      method: 'post'
    })
  },

  /**
   * 取消订单
   */
  cancelOrder(orderId: string) {
    return request<ApiResponse>({
      url: `/orders/${orderId}/cancel/`,
      method: 'post'
    })
  }
}
