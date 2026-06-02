<template>
  <div class="chat-window-container">
    <!-- 顶部导航栏 -->
    <header class="chat-header">
      <!-- 关联商品信息 -->
      <div class="header-goods" v-if="props.session?.goods" @click="goToGoods">
        <el-image
          class="goods-thumb"
          :src="props.session.goods.cover ? getImageUrl(props.session.goods.cover) : ''"
          fit="cover"
        >
          <template #error>
            <div class="goods-thumb-error"><el-icon><Picture /></el-icon></div>
          </template>
        </el-image>
        <div class="goods-info">
          <span class="goods-title">{{ props.session.goods.title || '查看商品' }}</span>
          <span class="goods-link">点击查看商品详情</span>
        </div>
        <el-icon class="goods-arrow" :size="14"><ArrowRight /></el-icon>
      </div>
      <div v-else class="header-placeholder">聊天中</div>
    </header>

    <!-- 中间消息区域 -->
    <main class="chat-messages" ref="messagesContainer">
      <!-- 用户身份未就绪时显示加载状态，防止空值判定导致布局错误 -->
      <div v-if="!isUserReady" class="messages-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      <template v-else>
      <!-- 加载提示 -->
      <div class="messages-start" v-if="messages.length > 0">
        <span class="start-line"></span>
        <span class="start-text">以上为历史消息</span>
        <span class="start-line"></span>
      </div>

      <div
        v-for="msg in messages"
        :key="msg.id"
        class="message-wrapper"
        :class="{ 'message-mine': isMyMessage(msg), 'message-other': !isMyMessage(msg) }"
      >
        <!-- 对方头像 (左侧) -->
        <el-avatar
          v-if="!isMyMessage(msg)"
          class="msg-avatar"
          :size="38"
          :src="getAvatarSrc(msg.sender.avatar)"
        />

        <!-- 消息气泡 -->
        <div class="msg-content">
          <div class="msg-bubble">{{ msg.content }}</div>
          <div class="msg-meta">
            <span class="msg-time">{{ formatTime(msg.created_at) }}</span>
            <span v-if="isMyMessage(msg)" class="msg-status" :class="{ 'is-read': msg.is_read }">
              {{ msg.is_read ? '已读' : '未读' }}
            </span>
          </div>
        </div>

        <!-- 我方头像 (右侧) -->
        <el-avatar
          v-if="isMyMessage(msg)"
          class="msg-avatar"
          :size="38"
          :src="getAvatarSrc(userStore.userAvatar)"
        />
      </div>
      </template>
    </main>

    <!-- 底部输入区域 -->
    <footer class="chat-footer">
      <div class="input-area">
        <el-input
          v-model="inputContent"
          type="textarea"
          :rows="3"
          placeholder="输入消息..."
          resize="none"
          @keydown.enter.prevent="handleSend"
        />
      </div>
      <div class="action-area">
        <span class="send-tip">Enter 发送</span>
        <el-button
          type="primary"
          class="send-btn"
          @click="handleSend"
          :disabled="!inputContent.trim()"
          round
        >
          <el-icon class="el-icon--left"><Position /></el-icon>发送
        </el-button>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Position, Picture, ArrowRight, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import chatApi, { type ChatMessage, type ChatSession } from '@/api/chatapi'
import { useUserStore } from '@/store/userstore'
import { getImageUrl } from '@/utils/format'
import { buildWsUrl } from '@/config/runtime'
import { openAuthDialog } from '@/composables/useAuthDialog'

const props = defineProps<{
  sessionId: string
  session?: ChatSession  // 从 ChatList 传入的完整会话信息
}>()

const emit = defineEmits(['message-sent'])

const router = useRouter()
const userStore = useUserStore()

const messages = ref<ChatMessage[]>([])
const inputContent = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

// 从 JWT token 中解码 user_id（兜底方案）
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

// 稳健的当前用户 ID：优先 Pinia store，兜底 localStorage，再兜底 JWT 解码
const currentUserId = computed<string | null>(() => {
  if (userStore.userId) return String(userStore.userId)
  const stored = localStorage.getItem('userId')
  if (stored) return stored
  return extractUserIdFromToken()
})

// 用户身份是否已就绪（决定是否渲染消息列表）
const isUserReady = computed(() => !!currentUserId.value)

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// ========== WebSocket 相关状态 ==========
let socket: WebSocket | null = null
let reconnectTimer: number | null = null
let reconnectAttempts = 0
const MAX_RECONNECT_ATTEMPTS = 5
const RECONNECT_BASE_DELAY = 2000  // 基础重连间隔 2 秒

// 获取头像 src
const getAvatarSrc = (avatar: string | null | undefined): string => {
  if (!avatar) return defaultAvatar
  const url = getImageUrl(avatar)
  return url || defaultAvatar
}

// 判断是否是我发的消息（统一转 String 比较，多层兜底防止类型不一致或状态未加载）
const isMyMessage = (msg: ChatMessage): boolean => {
  const myId = currentUserId.value
  if (!myId) return false
  return String(msg.sender?.id) === myId
}

// 跳转到商品详情
const goToGoods = () => {
  if (props.session?.goods?.id) {
    const route = router.resolve(`/goods/${props.session.goods.id}`)
    window.open(route.href, '_blank')
  }
}

// 格式化时间
const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 标记已读（HTTP 接口 + 本地同步）
const markAsRead = async () => {
  try {
    await chatApi.markReadAPI(props.sessionId)
    // 本地同步：将对方发给我的消息都标为已读
    messages.value.forEach(msg => {
      if (!isMyMessage(msg) && !msg.is_read) {
        msg.is_read = true
      }
    })
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

// ========== HTTP：拉取历史消息（仅首次进入时使用） ==========
const fetchHistoryMessages = async () => {
  try {
    const res = await chatApi.getMessagesAPI(props.sessionId)
    if (res.code === 200 && res.data) {
      messages.value = res.data
      scrollToBottom()
    }
  } catch (error) {
    console.error('拉取历史消息失败:', error)
  }
}

// ========== WebSocket：连接管理 ==========
const connectWebSocket = () => {
  // 关闭旧连接
  closeWebSocket()

  const token = localStorage.getItem('access')
  if (!token) {
    console.error('WebSocket: 未找到 token，无法连接')
    return
  }

  const wsUrl = buildWsUrl(`/ws/chats/${props.sessionId}/`, token)
  socket = new WebSocket(wsUrl)

  socket.onopen = () => {
    console.log('WebSocket 已连接:', props.sessionId)
    reconnectAttempts = 0  // 连接成功，重置重连计数
  }

  socket.onmessage = (event: MessageEvent) => {
    try {
      const payload = JSON.parse(event.data)

      // 服务端广播的新消息：{ type: 'chat.message', data: {...} }
      if (payload.type === 'chat.message' && payload.data) {
        const newMsg: ChatMessage = payload.data

        // 防止重复：检查消息 ID 是否已存在
        const exists = messages.value.some(m => m.id === newMsg.id)
        if (!exists) {
          // 优先检查是否是自己发送的乐观更新的回声（temp_ 前缀 + 内容一致）
          const tempIndex = messages.value.findIndex(
            m => String(m.id).startsWith('temp_') && m.content === newMsg.content
          )
          if (tempIndex !== -1) {
            // 服务端确认消息替换临时消息
            messages.value[tempIndex] = newMsg
          } else if (isMyMessage(newMsg)) {
            messages.value.push(newMsg)
          } else {
            // 对方发的消息，直接追加并标记已读
            messages.value.push(newMsg)
            markAsRead()
          }
          scrollToBottom()
          emit('message-sent')
        }
      }

      // 对方已读通知：{ type: 'messages.read', reader_id: '...' }
      if (payload.type === 'messages.read' && payload.reader_id) {
        // 对方读了我的消息 → 把我发的所有未读消息标为已读
        if (String(payload.reader_id) !== currentUserId.value) {
          messages.value.forEach(msg => {
            if (isMyMessage(msg) && !msg.is_read) {
              msg.is_read = true
            }
          })
        }
      }
    } catch (error) {
      console.error('WebSocket 消息解析失败:', error)
    }
  }

  socket.onclose = (event: CloseEvent) => {
    console.log('WebSocket 已断开:', event.code, event.reason)
    socket = null

    // 非正常关闭时尝试重连（code 1000 是正常关闭）
    if (event.code !== 1000) {
      scheduleReconnect()
    }
  }

  socket.onerror = (error: Event) => {
    console.error('WebSocket 错误:', error)
  }
}

// 计划重连（指数退避）
const scheduleReconnect = () => {
  if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
    console.warn('WebSocket 重连次数已达上限，停止重连')
    return
  }

  // 指数退避：2s, 4s, 8s, 16s, 32s
  const delay = RECONNECT_BASE_DELAY * Math.pow(2, reconnectAttempts)
  reconnectAttempts++

  console.log(`WebSocket 将在 ${delay / 1000}s 后尝试第 ${reconnectAttempts} 次重连...`)

  reconnectTimer = window.setTimeout(() => {
    connectWebSocket()
  }, delay)
}

// 关闭 WebSocket
const closeWebSocket = () => {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  if (socket) {
    socket.onclose = null  // 防止触发重连
    socket.close(1000, '组件卸载')
    socket = null
  }
}

// ========== 发送消息（通过 WebSocket） ==========
const handleSend = () => {
  const content = inputContent.value.trim()
  if (!content) return

  // 乐观更新 UI：先在本地显示消息（使用 temp_ 前缀标记临时消息）
  const tempId = `temp_${Date.now()}`
  const tempMsg: ChatMessage = {
    id: tempId,
    sender: {
      id: currentUserId.value!,
      nickname: userStore.userName,
      avatar: userStore.userAvatar
    },
    content: content,
    created_at: new Date().toISOString(),
    is_read: false
  }
  messages.value.push(tempMsg)
  inputContent.value = ''
  scrollToBottom()

  // 通过 WebSocket 发送
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ message: content }))
  } else {
    // WebSocket 不可用时回退到 HTTP
    chatApi.sendMessageAPI({
      session_id: props.sessionId,
      content: content
    }).then(res => {
      if (res.code === 200 && res.data) {
        const index = messages.value.findIndex(m => m.id === tempId)
        if (index !== -1) {
          messages.value[index] = res.data
        }
        emit('message-sent')
      } else {
        ElMessage.error(res.msg || '发送失败')
      }
    }).catch(error => {
      console.error('发送消息异常:', error)
    })
  }
}

// ========== 初始化聊天 ==========
const initChat = async () => {
  messages.value = []
  reconnectAttempts = 0

  // 1. 先通过 HTTP 拉取历史消息
  await fetchHistoryMessages()

  // 2. 标记已读
  markAsRead()

  // 3. 建立 WebSocket 连接，监听增量消息
  connectWebSocket()
}

// 切换会话时重新初始化
watch(() => props.sessionId, () => {
  initChat()
})

onMounted(() => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    openAuthDialog('login')
    return
  }
  initChat()
})

onUnmounted(() => {
  closeWebSocket()
})
</script>

<style scoped>
.chat-window-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background-color: #f5f7fa;
}

/* ===== 顶部 Header ===== */
.chat-header {
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #f0f2f5;
  flex-shrink: 0;
}

.header-placeholder {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 商品信息条 */
.header-goods {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px 8px 8px;
  background: #f8f9fb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #f0f2f5;
}

.header-goods:hover {
  background: #eef3ff;
  border-color: rgba(64, 158, 255, 0.2);
}

.goods-thumb {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  flex-shrink: 0;
}

.goods-thumb-error {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f0f2f5;
  color: #c0c4cc;
  font-size: 14px;
}

.goods-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.goods-title {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 260px;
}

.goods-link {
  font-size: 12px;
  color: #409eff;
}

.goods-arrow {
  color: #c0c4cc;
  flex-shrink: 0;
}

/* ===== 消息区域 ===== */
.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-messages::-webkit-scrollbar {
  width: 5px;
}
.chat-messages::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 4px;
}
.chat-messages::-webkit-scrollbar-thumb:hover {
  background-color: #c0c4cc;
}

/* 加载状态 */
.messages-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 0;
  color: #c0c4cc;
  font-size: 14px;
}

/* 历史消息分隔线 */
.messages-start {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.start-line {
  flex: 1;
  height: 1px;
  background: #e8eaed;
}

.start-text {
  font-size: 12px;
  color: #c0c4cc;
  white-space: nowrap;
}

/* 消息气泡 */
.message-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  max-width: 75%;
}

.message-other {
  align-self: flex-start;
  flex-direction: row;
}

.message-mine {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.msg-content {
  display: flex;
  flex-direction: column;
}

.message-mine .msg-content {
  align-items: flex-end;
}

.message-other .msg-content {
  align-items: flex-start;
}

.msg-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
  max-width: 100%;
}

.message-other .msg-bubble {
  background-color: #fff;
  color: #303133;
  border-top-left-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.message-mine .msg-bubble {
  background: linear-gradient(135deg, #409eff 0%, #5b8ff9 100%);
  color: #fff;
  border-top-right-radius: 4px;
  box-shadow: 0 1px 4px rgba(64, 158, 255, 0.25);
}

.msg-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
  padding: 0 2px;
}

.msg-time {
  font-size: 11px;
  color: #c0c4cc;
}

.msg-status {
  font-size: 11px;
  color: #f56c6c;
}

.msg-status.is-read {
  color: #c0c4cc;
}

/* ===== 底部输入区 ===== */
.chat-footer {
  background-color: #fff;
  border-top: 1px solid #f0f2f5;
  padding: 12px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}

.input-area :deep(.el-textarea__inner) {
  border: 1px solid #e8eaed;
  background-color: #fafbfd;
  box-shadow: none;
  padding: 10px 14px;
  font-size: 14px;
  border-radius: 10px;
  transition: all 0.2s ease;
}

.input-area :deep(.el-textarea__inner:focus) {
  background-color: #fff;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.action-area {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}

.send-tip {
  font-size: 12px;
  color: #c0c4cc;
}

.send-btn {
  padding: 8px 20px;
}
</style>
