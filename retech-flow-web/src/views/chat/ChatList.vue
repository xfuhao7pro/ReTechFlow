<template>
  <DecorativeBackground>
    <div class="chat-list-container">
      <div class="page-header">
        <div class="header-left">
          <el-icon class="header-icon"><ChatDotRound /></el-icon>
          <div>
            <h2>我的消息</h2>
            <p class="subtitle">交易沟通、系统通知统一收纳</p>
          </div>
        </div>

      </div>

      <div class="chat-body" v-loading="loading">
        <div class="chat-layout">
          <aside class="sidebar">
            <div class="sidebar-header">
              <span class="sidebar-title">会话</span>
              <span class="sidebar-count">{{ sessions.length }} 个联系人</span>
            </div>

            <template v-if="sessions.length > 0">
              <div class="session-list">
                <button
                  class="session-item"
                  v-for="session in sessions"
                  :key="session.id"
                  :class="{ 'is-active': activeSessionId === session.id }"
                  type="button"
                  @click="goToChat(session.id)"
                >
                  <div class="avatar-wrapper">
                    <el-badge :value="session.unread_count" :hidden="!session.unread_count" :max="99">
                      <el-avatar
                        :size="44"
                        :src="session.other_user?.avatar ? getImageUrl(session.other_user.avatar) : defaultAvatar"
                      />
                    </el-badge>
                  </div>

                  <div class="session-info">
                    <div class="info-top">
                      <span class="nickname">{{ session.other_user?.nickname || '神秘用户' }}</span>
                      <time>{{ formatTime(session.updated_at) }}</time>
                    </div>
                    <div class="info-bottom">
                      <span class="last-msg" :class="{ 'has-unread': session.unread_count > 0 }">
                        {{ session.unread_count > 0 ? `${session.unread_count} 条消息待查看` : (session.last_message || '暂无消息') }}
                      </span>
                    </div>
                  </div>

                  <el-image
                    v-if="session.goods?.cover"
                    class="session-goods"
                    :src="getImageUrl(session.goods.cover)"
                    fit="cover"
                    lazy
                  >
                    <template #error>
                      <div class="img-error"><el-icon><Picture /></el-icon></div>
                    </template>
                  </el-image>
                </button>
              </div>
            </template>

            <div v-else class="empty-sidebar">
              <el-empty description="暂无会话" :image-size="86">
                <el-button type="primary" round @click="$router.push('/market')">
                  <el-icon class="el-icon--left"><Search /></el-icon>去交易广场
                </el-button>
              </el-empty>
            </div>
          </aside>

          <main class="chat-main">
            <ChatWindow
              v-if="activeSessionId"
              :session-id="activeSessionId"
              :session="activeSession"
              :key="activeSessionId"
              @message-sent="fetchSessions"
            />
            <div v-else class="empty-chat">
              <div class="empty-chat-inner">
                <el-icon :size="46"><ChatRound /></el-icon>
                <p class="empty-text">选择一个会话开始沟通</p>
                <p class="empty-hint">左侧会话会按最近消息自动排序</p>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  </DecorativeBackground>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Picture, ChatDotRound, ChatRound, Search } from '@element-plus/icons-vue'
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

const activeSession = computed(() => {
  if (!activeSessionId.value) return undefined
  return sessions.value.find(s => s.id === activeSessionId.value)
})

const fetchSessions = async () => {
  try {
    const res = await chatApi.getSessionsAPI()
    if (res.code === 200 && res.data) {
      sessions.value = res.data

      if (!activeSessionId.value && sessions.value.length > 0) {
        const querySessionId = route.query.sessionId as string
        if (querySessionId && sessions.value.some(s => s.id === querySessionId)) {
          activeSessionId.value = querySessionId
        } else {
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

watch(() => route.query.sessionId, (newVal) => {
  if (newVal && typeof newVal === 'string') activeSessionId.value = newVal
}, { immediate: true })

const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const isToday = date.toDateString() === now.toDateString()

  if (isToday) return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })

  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) return '昨天'

  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

onMounted(() => {
  fetchSessions()
})
</script>

<style scoped>
.chat-list-container {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 24px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 26px;
  color: #2563eb;
  background: #eef4ff;
  padding: 10px;
  border-radius: 8px;
}

.page-header h2 {
  font-size: 22px;
  color: #172033;
  margin: 0 0 4px;
  font-weight: 700;
}

.subtitle {
  color: #64748b;
  font-size: 13px;
  margin: 0;
}

.chat-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  border-radius: 10px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
  background: #fff;
}

.chat-layout {
  display: flex;
  height: 100%;
  width: 100%;
}

.sidebar {
  width: 340px;
  border-right: 1px solid #edf1f5;
  display: flex;
  flex-direction: column;
  background: #fbfcfe;
}

.sidebar-header {
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 18px;
  border-bottom: 1px solid #edf1f5;
  background: #fff;
  flex-shrink: 0;
}

.sidebar-title {
  font-size: 15px;
  font-weight: 700;
  color: #172033;
}

.sidebar-count {
  color: #94a3b8;
  font-size: 12px;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-list::-webkit-scrollbar {
  width: 5px;
}

.session-list::-webkit-scrollbar-thumb {
  background-color: #d8dee8;
  border-radius: 4px;
}

.session-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  text-align: left;
}

.session-item:hover {
  background: #f3f7ff;
}

.session-item.is-active {
  background: #eef5ff;
  border-color: rgba(37, 99, 235, 0.18);
}

.avatar-wrapper {
  flex-shrink: 0;
}

.session-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.info-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.nickname {
  font-size: 14px;
  font-weight: 700;
  color: #172033;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-top time {
  font-size: 11px;
  color: #94a3b8;
  flex-shrink: 0;
}

.last-msg {
  display: block;
  max-width: 100%;
  font-size: 13px;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.last-msg.has-unread {
  color: #1d4ed8;
  font-weight: 700;
}

.session-goods {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #eef2f7;
  flex-shrink: 0;
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

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f6f8fb;
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
  color: #94a3b8;
}

.empty-text {
  font-size: 16px;
  color: #334155;
  margin: 8px 0 0;
  font-weight: 700;
}

.empty-hint {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

.avatar-wrapper :deep(.el-badge__content) {
  font-size: 10px;
}

@media (max-width: 980px) {
  .chat-list-container {
    padding: 14px;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .sidebar {
    width: 300px;
  }
}
</style>
