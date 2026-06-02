<template>
  <DecorativeBackground>
  <div class="chat-list-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><ChatDotRound /></el-icon>
        <div>
          <h2>我的消息</h2>
          <p class="subtitle">与买家/卖家的沟通记录都在这里</p>
        </div>
      </div>
    </div>

    <!-- 主体区域 -->
    <div class="chat-body" v-loading="loading">
      <div class="chat-layout">
        <!-- 左侧会话列表 -->
        <div class="sidebar">
          <div class="sidebar-header">
            <span class="sidebar-title">消息</span>
            <el-badge :value="totalUnread" :hidden="!totalUnread" class="unread-total-badge">
              <el-icon :size="18" color="#909399"><Bell /></el-icon>
            </el-badge>
          </div>

          <template v-if="sessions.length > 0">
            <div class="session-list">
              <div
                class="session-item"
                v-for="session in sessions"
                :key="session.id"
                :class="{ 'is-active': activeSessionId === session.id }"
                @click="goToChat(session.id)"
              >
                <!-- 头像 + 未读气泡 -->
                <div class="avatar-wrapper">
                  <el-badge :value="session.unread_count" :hidden="!session.unread_count" :max="99">
                    <el-avatar
                      :size="44"
                      :src="session.other_user?.avatar ? getImageUrl(session.other_user.avatar) : defaultAvatar"
                    />
                  </el-badge>
                  <span class="online-dot"></span>
                </div>

                <!-- 昵称 + 最后消息 -->
                <div class="session-info">
                  <div class="info-top">
                    <span class="nickname">{{ session.other_user?.nickname || '神秘用户' }}</span>
                    <span class="time">{{ formatTime(session.updated_at) }}</span>
                  </div>
                  <div class="info-bottom">
                    <span class="last-msg" :class="{ 'has-unread': session.unread_count > 0 }">
                      {{ session.last_message || '暂无消息' }}
                    </span>
                  </div>
                </div>

                <!-- 商品缩略图 -->
                <div class="session-goods" v-if="session.goods && session.goods.cover">
                  <el-image
                    class="goods-cover"
                    :src="getImageUrl(session.goods.cover)"
                    fit="cover"
                    lazy
                  >
                    <template #error>
                      <div class="img-error"><el-icon><Picture /></el-icon></div>
                    </template>
                  </el-image>
                </div>
              </div>
            </div>
          </template>

          <div v-else class="empty-sidebar">
            <el-empty description="暂无消息记录" :image-size="80">
              <el-button type="primary" round @click="$router.push('/market')">
                <el-icon class="el-icon--left"><Search /></el-icon>去逛逛
              </el-button>
            </el-empty>
          </div>
        </div>

        <!-- 右侧聊天窗口 -->
        <div class="chat-main">
          <ChatWindow
            v-if="activeSessionId"
            :session-id="activeSessionId"
            :session="activeSession"
            :key="activeSessionId"
            @message-sent="fetchSessions"
          />
          <div v-else class="empty-chat">
            <div class="empty-chat-inner">
              <el-icon :size="48" color="#c0c4cc"><ChatRound /></el-icon>
              <p class="empty-text">选择左侧会话开始聊天</p>
              <p class="empty-hint">点击任意会话即可查看消息</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </DecorativeBackground>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Picture, ChatDotRound, ChatRound, Bell, Search } from '@element-plus/icons-vue'
import chatApi, { type ChatSession } from '@/api/chatapi'
import { getImageUrl } from '@/utils/format'
import ChatWindow from './ChatWindow.vue'
import DecorativeBackground from '@/components/DecorativeBackground.vue'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const sessions = ref<ChatSession[]>([])
const activeSessionId = ref<string>('')

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 全部未读总数
const totalUnread = computed(() => {
  return sessions.value.reduce((sum, s) => sum + (s.unread_count || 0), 0)
})

// 当前选中的会话对象（传给 ChatWindow 用于显示对方信息）
const activeSession = computed(() => {
  if (!activeSessionId.value) return undefined
  return sessions.value.find(s => s.id === activeSessionId.value)
})

const fetchSessions = async () => {
  try {
    const res = await chatApi.getSessionsAPI()
    if (res.code === 200 && res.data) {
      sessions.value = res.data

      // 如果当前还没有选中会话
      if (!activeSessionId.value && sessions.value.length > 0) {
        const querySessionId = route.query.sessionId as string
        if (querySessionId && sessions.value.some(s => s.id === querySessionId)) {
          // 路由带了 sessionId，尝试自动选中
          activeSessionId.value = querySessionId
        } else {
          // 默认选中第一条会话
          const firstSession = sessions.value[0]
          if (firstSession) {
            activeSessionId.value = firstSession.id
            router.replace({ query: { ...route.query, sessionId: firstSession.id } })
          }
        }
      }
    }
  } catch (error) {
    console.error('获取会话列表失败:', error)
  } finally {
    loading.value = false
  }
}

const goToChat = (sessionId: string) => {
  activeSessionId.value = sessionId
  router.replace({ query: { ...route.query, sessionId } })
  fetchSessions()
}

// 监听路由变化
watch(() => route.query.sessionId, (newVal) => {
  if (newVal && typeof newVal === 'string') {
    activeSessionId.value = newVal
  }
}, { immediate: true })

const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const isToday = date.toDateString() === now.toDateString()

  if (isToday) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  // 判断是否是昨天
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  }

  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

onMounted(() => {
  fetchSessions()
})
</script>

<style scoped>
.chat-list-container {
  animation: fadeIn 0.3s ease;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ===== 页面标题 ===== */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 28px;
  color: #409eff;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.12), rgba(138, 101, 255, 0.08));
  padding: 10px;
  border-radius: 12px;
}

.page-header h2 {
  font-size: 20px;
  color: #1f2f47;
  margin: 0 0 2px;
  font-weight: 700;
}

.subtitle {
  color: #909399;
  font-size: 13px;
  margin: 0;
}

/* ===== 主体布局 ===== */
.chat-body {
  flex: 1;
  min-height: 0;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(64, 158, 255, 0.1);
  box-shadow: 0 2px 12px rgba(31, 49, 85, 0.06);
  background: #fff;
}

.chat-layout {
  display: flex;
  height: 100%;
  width: 100%;
}

/* ===== 左侧会话列表 ===== */
.sidebar {
  width: 320px;
  border-right: 1px solid #f0f2f5;
  display: flex;
  flex-direction: column;
  background-color: #fafbfd;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f2f5;
  background: #fff;
  flex-shrink: 0;
}

.sidebar-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.session-list {
  flex: 1;
  overflow-y: auto;
}

/* 滚动条 */
.session-list::-webkit-scrollbar {
  width: 4px;
}
.session-list::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 4px;
}
.session-list::-webkit-scrollbar-thumb:hover {
  background-color: #c0c4cc;
}

.session-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid #f5f6f8;
  position: relative;
}

.session-item:hover:not(.is-active) {
  background-color: #f0f4ff;
}

.session-item.is-active {
  background: linear-gradient(90deg, rgba(64, 158, 255, 0.1) 0%, rgba(64, 158, 255, 0.04) 100%);
  border-left: 3px solid #409eff;
  padding-left: 13px;
}

.session-item:last-child {
  border-bottom: none;
}

/* 头像 */
.avatar-wrapper {
  position: relative;
  margin-right: 12px;
  flex-shrink: 0;
}

.online-dot {
  position: absolute;
  bottom: 1px;
  right: 1px;
  width: 10px;
  height: 10px;
  background: #67c23a;
  border: 2px solid #fff;
  border-radius: 50%;
  display: none; /* 预留在线状态，暂不启用 */
}

/* 会话信息 */
.session-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
}

.info-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nickname {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 130px;
}

.is-active .nickname {
  color: #409eff;
}

.time {
  font-size: 11px;
  color: #c0c4cc;
  flex-shrink: 0;
  margin-left: 8px;
}

.info-bottom {
  display: flex;
}

.last-msg {
  font-size: 13px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.last-msg.has-unread {
  color: #606266;
  font-weight: 500;
}

/* 商品缩略图 */
.session-goods {
  margin-left: 10px;
  width: 42px;
  height: 42px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #f0f2f5;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.goods-cover {
  width: 100%;
  height: 100%;
}

.img-error {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #c0c4cc;
  font-size: 16px;
}

.empty-sidebar {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ===== 右侧聊天区 ===== */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  position: relative;
  min-width: 0;
}

.empty-chat {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.empty-chat-inner {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.empty-text {
  font-size: 16px;
  color: #606266;
  margin: 8px 0 0;
  font-weight: 500;
}

.empty-hint {
  font-size: 13px;
  color: #c0c4cc;
  margin: 0;
}

/* Badge 样式微调 */
.avatar-wrapper :deep(.el-badge__content) {
  font-size: 11px;
  padding: 0 5px;
  height: 16px;
  line-height: 16px;
}

.unread-total-badge :deep(.el-badge__content) {
  font-size: 10px;
}
</style>
