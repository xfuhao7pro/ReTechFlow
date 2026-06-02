/**
 * 估价 WebSocket Store 工厂
 *
 * 封装 WebSocket 连接管理 + 估价任务状态。
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElNotification } from 'element-plus'
import goodsApi, { type ValuationResult } from '@/api/goodsapi'
import { buildWsUrl } from '@/config/runtime'

export { type ValuationResult }

export function createValuationStore(storeId: string, label: string) {
  return defineStore(storeId, () => {
    // ---- 估价状态 ----
    const isValuating = ref(false)
    const currentTaskId = ref<string | null>(null)
    const valuationResult = ref<ValuationResult | null>(null)
    const valuationError = ref<string | null>(null)

    // 标记用户是否在对应页面（由页面组件维护）
    const isOnPage = ref(false)

    // ---- WebSocket 连接 ----
    let socket: WebSocket | null = null
    let reconnectTimer: number | null = null
    let pollTimer: number | null = null
    let reconnectAttempts = 0
    const MAX_RECONNECT = 5
    const RECONNECT_BASE_DELAY = 2000

    /** 建立估价专用 WebSocket 连接 */
    function connectWS() {
      closeWS()

      const token = localStorage.getItem('access')
      if (!token) return

      const wsUrl = buildWsUrl('/ws/valuation/', token)
      socket = new WebSocket(wsUrl)

      socket.onopen = () => {
        console.log(`[${label}WS] 已连接`)
        reconnectAttempts = 0
      }

      socket.onmessage = (event: MessageEvent) => {
        try {
          const payload = JSON.parse(event.data)
          handleWsMessage(payload)
        } catch (e) {
          console.error(`[${label}WS] 消息解析失败:`, e)
        }
      }

      socket.onclose = (event: CloseEvent) => {
        console.log(`[${label}WS] 已断开:`, event.code)
        socket = null
        if (event.code !== 1000) {
          scheduleReconnect()
        }
      }

      socket.onerror = (error: Event) => {
        console.error(`[${label}WS] 错误:`, error)
      }
    }

    function scheduleReconnect() {
      if (reconnectAttempts >= MAX_RECONNECT) return
      const delay = RECONNECT_BASE_DELAY * Math.pow(2, reconnectAttempts)
      reconnectAttempts++
      reconnectTimer = window.setTimeout(() => connectWS(), delay)
    }

    function closeWS() {
      if (reconnectTimer) {
        clearTimeout(reconnectTimer)
        reconnectTimer = null
      }
      if (socket) {
        socket.onclose = null
        socket.close(1000, '主动关闭')
        socket = null
      }
    }

    function stopPolling() {
      if (pollTimer) {
        clearInterval(pollTimer)
        pollTimer = null
      }
    }

    function startPolling(taskId: string) {
      stopPolling()
      pollTimer = window.setInterval(async () => {
        if (currentTaskId.value !== taskId) {
          stopPolling()
          return
        }

        try {
          const response = await goodsApi.getValuationResultAPI(taskId)
          if (response.code !== 200 || response.data.status === '计算中') return

          handleWsMessage({
            type: 'valuation_result',
            task_id: taskId,
            status: response.data.status,
            msg: response.msg,
            data: response.data.result
          })
        } catch {
          // The request interceptor already reports unexpected failures.
        }
      }, 3000)
    }

    /** 处理 WebSocket 推送的估价结果 */
    function handleWsMessage(payload: any) {
      if (payload.type !== 'valuation_result') return

      const taskId = payload.task_id as string

      // 如果 task_id 不匹配当前任务（已被取消），静默丢弃
      if (taskId !== currentTaskId.value) {
        console.log(`[${label}WS] 收到已取消任务的结果，静默丢弃:`, taskId)
        return
      }

      if (payload.status === '成功' && payload.data) {
        valuationResult.value = payload.data as ValuationResult
        valuationError.value = null
        isValuating.value = false
        stopPolling()

        // 如果用户不在对应页面，弹出全局通知
        if (!isOnPage.value) {
          const price = Math.floor(
            (payload.data.min_price + payload.data.max_price) / 2
          )
          ElNotification({
            title: '估价完成',
            message: `您的商品估价已出：约 ¥${price} 元`,
            type: 'success',
            duration: 8000
          })
        }
      } else {
        valuationError.value = payload.msg || '估价失败，请重试'
        valuationResult.value = null
        isValuating.value = false
        stopPolling()

        if (!isOnPage.value) {
          ElNotification({
            title: '估价失败',
            message: payload.msg || '估价失败，请重试',
            type: 'error',
            duration: 5000
          })
        }
      }
    }

    /** 提交估价任务（由页面调用 HTTP POST 后设置 taskId） */
    function startTask(taskId: string) {
      currentTaskId.value = taskId
      valuationResult.value = null
      valuationError.value = null
      isValuating.value = true
      startPolling(taskId)
    }

    /** 障眼法取消：清空前端状态，后端继续算但结果会被静默丢弃 */
    function cancelTask() {
      currentTaskId.value = null
      valuationResult.value = null
      valuationError.value = null
      isValuating.value = false
      stopPolling()
    }

    /** 完全重置（退出登录或完成发布时调用） */
    function reset() {
      cancelTask()
      // 如果不传参数，默认也关闭 WS。如果只是想清空结果，可单独调 cancelTask
      // 但在工厂模式下，这里通常用于彻底清理
      closeWS()
    }

    /** 清空结果和错误信息，保留 WS 连接 */
    function clearResults() {
      valuationResult.value = null
      valuationError.value = null
    }

    return {
      // state
      isValuating,
      currentTaskId,
      valuationResult,
      valuationError,
      isOnPage,
      // actions
      connectWS,
      closeWS,
      startTask,
      cancelTask,
      reset,
      clearResults
    }
  })
}
