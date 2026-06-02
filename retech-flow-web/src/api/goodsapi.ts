import request from '../utils/request'

// 定义通用的响应结构接口
export interface ApiResponse<T = any> {
  code: number
  msg: string
  data: T
  errors?:string
}
// 请求-智能估价接口
export interface ValuationData {
  user_desc:string
  image_paths:string[]
}
// 响应-智能估价接口（异步提交，返回 task_id）
export interface ValuationSubmitResult {
  task_id: string
}

export interface ValuationTaskResult {
  task_id: string
  status: string
  result: ValuationResult | null
}

// WebSocket 推送的估价最终结果
export interface ValuationResult {
  title: string
  description: string
  min_price: number
  max_price: number
}
// 上传图片接口
export interface ImageData{
    image:string
}
// 响应图片接口
export interface UploadResult {
  file_path: string
  url: string
}

// 上传图片api
const uploadImageAPI = (data:FormData)=>{
    return request<ApiResponse<UploadResult>>({
        url: '/goods/up-image/',
        method: 'post',
        data: data,
        headers: {
      'Content-Type': 'multipart/form-data'
    }
      })
}
// ai估价api（异步提交，瞬间返回 task_id）
const valuationAPI = (data: ValuationData) => {
  return request<ApiResponse<ValuationSubmitResult>>({
    url: '/goods/ai-evaluation/',
    method: 'post',
    data: data
  })
}

const getValuationResultAPI = (taskId: string) => {
  return request<ApiResponse<ValuationTaskResult>>({
    url: `/goods/ai-evaluation/${taskId}/`,
    method: 'get'
  })
}
// 发布接口
export interface CreateGoodsData {
  title: string
  description: string
  price: number
  category_id: number
  attributes: Record<string, string>
  temp_images: string[]
  delivery_method?: number
  status?: number
}

const createGoodsAPI = (data: CreateGoodsData) => {
  return request<ApiResponse<any>>({
    url: '/goods/create/', 
    method: 'post',
    data: data
  })
}

const saveDraftAPI = (data: CreateGoodsData) => {
  return request<ApiResponse<any>>({
    url: '/goods/draft/', 
    method: 'post',
    data: data
  })
}

export type MyPublishedStatus = 'on_sale' | 'sold' | 'offline' | 'draft'

export interface MyPublishedItem {
  id: string
  title: string
  price: number
  cover: string
  status: number
  statusText: string
  views?: number
  is_like?: boolean
  detailPath?: string
}

export interface MyPublishedListData {
  list: MyPublishedItem[]
}

/** 获取分类字典接口 */
export interface CategoryAttribute {
  name: string
  options: string[]
}

export interface CategoryData {
  id: number
  name: string
  sort: number
  attributes: CategoryAttribute[]
}

const getCategoriesAPI = () => {
  return request<ApiResponse<CategoryData[]>>({
    url: '/goods/categories/',
    method: 'get'
  })
}

/** 获取当前用户已发布商品（后端路径可按实际调整） */
const listMyPublishedAPI = (params?: { status?: number | string, keyword?: string }) => {
  return request<ApiResponse<any>>({
    url: '/goods/my-list/',
    method: 'get',
    params
  })
}

/** 获取商品详情 */
const getGoodsDetailAPI = (id: string) => {
  return request<ApiResponse<any>>({
    url: `/goods/${id}/`,
    method: 'get'
  })
}

/** 获取所有商品列表（广场页） */
const getGoodsListAPI = (params?: any) => {
  return request<ApiResponse<any>>({
    url: '/goods/list/',
    method: 'get',
    params
  })
}

/** 切换收藏状态 */
export interface ToggleLikeData {
  goods_id: number
}

export interface ToggleLikeResult {
  is_like: boolean
}

const toggleLikeAPI = (data: ToggleLikeData) => {
  return request<ApiResponse<ToggleLikeResult>>({
    url: '/goods/like/toggle/',
    method: 'post',
    data
  })
}

/** 获取我的收藏列表 */
const getMyLikesAPI = () => {
  return request<ApiResponse<any>>({
    url: '/goods/like/list/',
    method: 'get'
  })
}

/** 删除商品接口 */
const deleteGoodsAPI = (goodsId: string) => {
  return request<ApiResponse<any>>({
    url: '/goods/delete/',
    method: 'post',
    data: { goods_id: goodsId }
  })
}

export default {
  valuationAPI,
  getValuationResultAPI,
  uploadImageAPI,
  createGoodsAPI,
  saveDraftAPI,
  listMyPublishedAPI,
  getCategoriesAPI,
  getGoodsListAPI,
  getGoodsDetailAPI,
  toggleLikeAPI,
  getMyLikesAPI,
  deleteGoodsAPI
}
