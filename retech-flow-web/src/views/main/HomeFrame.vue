<template>
  <div class="common-layout">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <!-- 左侧：Logo/图片 -->
          <div class="header-left">
            <el-image
              class="header-logo"
              :src="logo"
              fit="contain"
              alt="图片走丢了！:("
            >
              <template #error>
                <div class="image-slot">
                  <p>图片走丢了！:(</p>
                </div>
              </template>
            </el-image>
          </div>

          <!-- 中间组件 -->
          <div class="header-center">
            <router-link to="/home" class="nav-link">首页</router-link>
            <router-link to="/valuation" class="nav-link">智能估价</router-link>
            <router-link to="/market" class="nav-link">交易广场</router-link>
            <router-link to="/orders" class="nav-link">我的订单</router-link>
          </div>

          <!-- 右侧登录/注册组件 -->
          <div class="header-right">
            <template v-if="!isLoggedIn">
              <button class="auth-btn login" @click="openAuthDialog('login')">登录</button>
              <button class="auth-btn register" @click="openAuthDialog('register')">注册</button>
            </template>
            <template v-else>
              <el-popover
                placement="bottom"
                :width="200"
                trigger="hover"
                popper-class="user-popover"
              >
                <template #reference>
                  <div class="user-info-trigger">
                    <el-avatar 
                      :size="32" 
                      :src="getSafeAvatarUrl(userAvatar)" 
                      class="user-avatar" 
                    >
                      <img v-if="!userAvatar" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png"/>
                    </el-avatar>
                    <span class="user-name">{{ userName }}</span>
                    <el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </div>
                </template>
                
                <div class="user-menu">
                  <div 
                    v-for="item in menuItems" 
                    :key="item.key" 
                    class="menu-item"
                    :class="{ 'divided': item.divided }"
                    @click="handleCommand(item.key)"
                  >
                    <el-icon v-if="item.icon" class="menu-icon"><component :is="item.icon" /></el-icon>
                    <span>{{ item.label }}</span>
                  </div>
                </div>
              </el-popover>

              <!-- 消息通知按钮 -->
              <div
                ref="messageEntryRef"
                class="message-entry"
                @mouseenter="openMessagePreview"
                @mouseleave="closeMessagePreview"
              >
                <button
                  class="message-bell"
                  :class="{ 'is-open': messagePanelVisible }"
                  type="button"
                  @click="toggleMessagePanel"
                >
                  <el-badge :value="messageBadgeCount" :hidden="messageBadgeCount === 0" :max="99">
                    <el-icon :size="22"><Bell /></el-icon>
                  </el-badge>
                </button>

                <transition name="message-pop">
                  <section
                    v-if="messagePanelVisible"
                    class="message-panel"
                    :style="messagePanelStyle"
                    @mouseenter="openMessagePreview"
                    @mouseleave="closeMessagePreview"
                  >
                    <header>
                      <div>
                        <strong>通知</strong>
                        <span>{{ totalUnread > 0 ? `${totalUnread} 条私信未读` : '暂无未读私信' }}</span>
                      </div>
                      <button v-if="messagePanelPinned" type="button" @click.stop="messagePanelPinned = false">关闭</button>
                    </header>

                    <button class="customer-summary" type="button" @click="goMessages">
                      <el-icon><ChatDotRound /></el-icon>
                      <span>{{ totalUnread > 0 ? `${totalUnread} 条私信未读` : '查看私信' }}</span>
                    </button>

                    <div class="system-title">
                      <strong>平台通知</strong>
                      <span>{{ announcements.length }}</span>
                    </div>

                    <div v-if="announcements.length" class="notice-list">
                      <article v-for="notice in announcements" :key="notice.id" class="notice-card">
                        <div class="notice-card-head">
                          <strong>{{ notice.title }}</strong>
                          <time>{{ formatNoticeTime(notice.created_at) }}</time>
                        </div>
                        <p>{{ notice.content }}</p>
                      </article>
                    </div>
                    <div v-else class="empty-notice">暂无系统通知</div>
                  </section>
                </transition>
              </div>
            </template>
          </div>
        </div>
      </el-header>

      <el-main>
        <div class="main-content">
          <router-view v-slot="{ Component }">
            <keep-alive :include="['Valuation', 'OrdersFrame']">
              <component :is="Component" />
            </keep-alive>
          </router-view>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script lang="ts" setup name="homeframe">
import { useRouter } from 'vue-router'
import logo from '../../assets/icon.png'
import { useUserStore } from '@/store/userstore'
import { useValuationStore } from '@/store/valuationStore'
import { storeToRefs } from 'pinia'
import { getImageUrl } from '@/utils/format'
import chatApi, { type SystemAnnouncement } from '@/api/chatapi'
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { openAuthDialog } from '@/composables/useAuthDialog'
import {
  User,
  ShoppingBag,
  Goods,
  Star,
  SwitchButton,
  ArrowDown,
  DocumentAdd,
  Bell,
  ChatDotRound
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const valuationStore = useValuationStore()
// 使用storeToRefs保持响应性
const { isLoggedIn, userName, userAvatar } = storeToRefs(userStore)

const totalUnread = ref(0)
const announcements = ref<SystemAnnouncement[]>([])
const messagePanelVisible = ref(false)
const messagePanelPinned = ref(false)
const messageEntryRef = ref<HTMLElement | null>(null)
const messagePanelPosition = ref({ top: 58, left: 12, width: 360 })
let unreadTimer: number | null = null

const messageBadgeCount = computed(() => totalUnread.value + announcements.value.length)
const messagePanelStyle = computed(() => ({
  top: `${messagePanelPosition.value.top}px`,
  left: `${messagePanelPosition.value.left}px`,
  width: `${messagePanelPosition.value.width}px`,
}))

const updateMessagePanelPosition = () => {
  const entry = messageEntryRef.value
  if (!entry) return
  const rect = entry.getBoundingClientRect()
  const edge = 12
  const gap = 10
  const width = Math.min(360, Math.max(0, window.innerWidth - edge * 2))
  const preferredLeft = rect.right + gap
  const left = Math.max(edge, Math.min(preferredLeft, window.innerWidth - width - edge))
  messagePanelPosition.value = {
    top: Math.max(edge, rect.bottom + 12),
    left,
    width,
  }
}

const fetchUnreadCount = async () => {
  if (!isLoggedIn.value) return
  try {
    const res = await chatApi.getSessionsAPI()
    if (res.code === 200 && res.data) {
      totalUnread.value = res.data.reduce((acc, curr) => acc + (curr.unread_count || 0), 0)
    }
  } catch (err) {
    console.error('获取未读消息失败', err)
  }
}

const fetchAnnouncements = async () => {
  if (!isLoggedIn.value) return
  try {
    const res = await chatApi.getSystemAnnouncementsAPI()
    if (res.code === 200 && res.data) announcements.value = res.data
  } catch (err) {
    console.error('获取系统通知失败', err)
  }
}

watch(isLoggedIn, (newVal) => {
  // 先清除旧的定时器，防止重复创建
  if (unreadTimer) {
    clearInterval(unreadTimer)
    unreadTimer = null
  }
  if (newVal) {
    fetchUnreadCount()
    fetchAnnouncements()
    unreadTimer = window.setInterval(fetchUnreadCount, 30000)
    // 建立估价 WebSocket 连接（全局生命周期，登录即连）
    valuationStore.connectWS()
  } else {
    totalUnread.value = 0
    announcements.value = []
    messagePanelVisible.value = false
    messagePanelPinned.value = false
    // 退出登录时断开估价 WS 并重置状态
    valuationStore.reset()
  }
}, { immediate: true })

onUnmounted(() => {
  if (unreadTimer) clearInterval(unreadTimer)
  window.removeEventListener('resize', updateMessagePanelPosition)
  valuationStore.closeWS()
})

onMounted(() => {
  window.addEventListener('resize', updateMessagePanelPosition)
})

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 获取安全的头像URL
const getSafeAvatarUrl = (avatarPath: string) => {
  if (!avatarPath) return defaultAvatar
  // 使用之前抽离的全局 getImageUrl 工具函数来处理后端返回的相对路径
  return getImageUrl(avatarPath)
}

const openMessagePreview = () => {
  updateMessagePanelPosition()
  messagePanelVisible.value = true
}

const closeMessagePreview = () => {
  if (!messagePanelPinned.value) messagePanelVisible.value = false
}

const toggleMessagePanel = () => {
  updateMessagePanelPosition()
  messagePanelPinned.value = !messagePanelPinned.value
  messagePanelVisible.value = messagePanelPinned.value || !messagePanelVisible.value
}

const goMessages = () => {
  messagePanelVisible.value = false
  messagePanelPinned.value = false
  router.push('/orders/messages')
}

const formatNoticeTime = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 菜单配置 - 解耦设计，方便后续添加
const menuItems = [
  { key: 'bought', label: '我买到的', icon: ShoppingBag, path: '/orders/bought' },
  { key: 'sold', label: '我卖出的', icon: Goods, path: '/orders/sold' },
  { key: 'published', label: '我发布的', icon: DocumentAdd, path: '/orders/published' },
  { key: 'favorites', label: '我的收藏', icon: Star, path: '/orders/favorites' },
  { key: 'profile', label: '个人资料', icon: User, path: '/orders/profile' },
  { key: 'logout', label: '退出登录', icon: SwitchButton, divided: true },
]

// 处理菜单点击
const handleCommand = (command: string) => {
  const item = menuItems.find(i => i.key === command)
  if (!item) return

  if (command === 'logout') {
    handleLogout()
  } else if (item.path) {
    router.push(item.path)
  }
}

// 退出登录处理
const handleLogout = () => {
  userStore.logout()
  router.push('/home')
}
</script>

<style scoped>
.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-shrink: 0; /* 防止挤压折行 */
}

.message-entry {
  position: relative;
  display: flex;
  align-items: center;
}

.message-bell {
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #fff;
  border: 0;
  background: transparent;
  border-radius: 6px;
  padding: 0;
  transition: color 0.2s ease, background 0.2s ease;
}

.message-bell:hover,
.message-bell.is-open {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.12);
}

.message-panel {
  position: fixed;
  right: auto;
  display: flex;
  box-sizing: border-box;
  max-height: min(520px, calc(100dvh - 76px));
  flex-direction: column;
  z-index: 50;
  padding: 0;
  color: #1f2937;
  background: #fff;
  border: 1px solid #dce3ec;
  border-radius: 8px;
  box-shadow: 0 16px 40px rgba(22, 34, 55, 0.16), 0 2px 8px rgba(22, 34, 55, 0.06);
  overflow: hidden;
  transform-origin: top right;
}

.message-panel header {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px 12px;
  border-bottom: 1px solid #eef2f6;
}

.message-panel header div {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.message-panel header strong {
  font-size: 15px;
  color: #111827;
  font-weight: 700;
}

.message-panel header span {
  color: #6b7280;
  font-size: 12px;
}

.message-panel header button {
  border: 0;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  font-size: 12px;
  padding: 0;
}

.message-panel header button:hover {
  color: #111827;
}

.customer-summary {
  flex: 0 0 auto;
  width: calc(100% - 24px);
  margin: 12px;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  color: #334155;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
}

.customer-summary:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.system-title {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #111827;
  margin: 0;
  padding: 0 16px 8px;
}

.system-title strong {
  font-size: 14px;
}

.system-title span {
  color: #94a3b8;
  font-size: 12px;
}

.notice-list {
  display: flex;
  min-height: 0;
  flex-direction: column;
  gap: 0;
  max-height: min(320px, calc(100dvh - 242px));
  overflow-y: auto;
  overscroll-behavior: contain;
  border-top: 1px solid #f1f5f9;
  scrollbar-gutter: stable;
}

.notice-list::-webkit-scrollbar {
  width: 5px;
}

.notice-list::-webkit-scrollbar-thumb {
  background-color: #d8dee8;
  border-radius: 4px;
}

.notice-card {
  padding: 12px 16px;
  border-radius: 0;
  background: #fff;
  border: 0;
  border-bottom: 1px solid #f1f5f9;
}

.notice-card:hover {
  background: #f8fafc;
}

.notice-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.notice-card-head strong {
  color: #111827;
  font-size: 14px;
  line-height: 1.4;
}

.notice-card-head time {
  color: #94a3b8;
  font-size: 11px;
  white-space: nowrap;
}

.notice-card p {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
  overflow-wrap: anywhere;
}

.empty-notice {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 86px;
  color: #94a3b8;
  font-size: 13px;
}

.message-pop-enter-active,
.message-pop-leave-active {
  transition:
    opacity 0.24s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.24s cubic-bezier(0.22, 1, 0.36, 1);
}

.message-pop-enter-from,
.message-pop-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.97);
}

@media (max-width: 760px) {
  .message-panel {
    max-height: calc(100dvh - 70px);
    transform-origin: top right;
  }

  .message-panel header {
    padding: 13px 14px 11px;
  }

  .customer-summary {
    width: calc(100% - 20px);
    margin: 10px;
  }

  .system-title {
    padding: 0 14px 8px;
  }

  .notice-list {
    max-height: calc(100dvh - 226px);
  }

  .notice-card {
    padding: 12px 14px;
  }

  .notice-card-head {
    display: grid;
    gap: 3px;
  }

  .notice-card-head time {
    white-space: normal;
  }
}

@media (prefers-reduced-motion: reduce) {
  .message-pop-enter-active,
  .message-pop-leave-active {
    transition-duration: 0.01ms;
  }
}

.user-info-trigger {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 20px;
  transition: all 0.3s;
  outline: none !important; 
}

/* 去除focus时的默认样式 */
.user-info-trigger:focus-visible {
  outline: none;
}

.user-info-trigger:hover {
  background-color: rgba(255, 255, 255, 0.28);
}

.user-avatar {
  margin-right: 8px;
  border: 1px solid #dcdfe6;
}

.user-name {
  margin-right: 5px;
  color: #f3f9ff;
  font-weight: 500;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100px;
}

/* 气泡菜单样式 */
.user-menu {
  padding: 5px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: background-color 0.2s;
  border-radius: 4px;
}

.menu-item:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.menu-item.divided {
  margin-top: 5px;
  border-top: 1px solid #ebeef5;
  padding-top: 10px;
}

.menu-icon {
  margin-right: 8px;
  font-size: 16px;
}


.nav-link {
  text-decoration: none;
  color: rgba(238, 247, 255, 0.98);
  font-size: 16px; /* 增大字号 14px -> 16px */
  padding: 0 15px;
  height: 40px;
  line-height: 40px;
  display: inline-block;
  transition: color 0.3s, text-shadow 0.3s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #ffffff;
  font-weight: 500;
  text-shadow: 0 0 14px rgba(122, 229, 255, 0.42);
}

.auth-btn {
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  padding: 8px 20px;
  border-radius: 4px;
  font-size: 16px; /* 增大字号 14px -> 16px */
  margin-left: 10px;
  transition: all 0.3s;
}

.auth-btn.login {
  color: #409eff;
  background-color: #ecf5ff;
  border: 1px solid #d9ecff;
}

.auth-btn.login:hover {
  background-color: #409eff;
  color: #fff;
  border-color: #409eff;
}

.auth-btn.register {
  color: #fff;
  background-color: #409eff;
  border: 1px solid #409eff;
}

.auth-btn.register:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

/* logo */
.header-logo {
  height: 50px;
  width: auto;
}

.common-layout {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow-x: clip;
}

.common-layout > .el-container {
  flex: 1;
  min-height: 0;
}

.el-container {
  height: 100%;
  min-height: 0;
}

.header {
  height: 80px;
  background:
    radial-gradient(circle at 8% 16%, rgba(103, 242, 255, 0.27), transparent 38%),
    radial-gradient(circle at 88% 14%, rgba(178, 151, 255, 0.24), transparent 40%),
    linear-gradient(118deg, #36598a 0%, #436ba0 48%, #4b75ae 100%);
  border-bottom: 1px solid rgba(174, 230, 255, 0.5);
  box-shadow: 0 7px 16px rgba(34, 68, 111, 0.2), inset 0 1px 0 rgba(220, 245, 255, 0.25);
  padding: 0; 
}

.header-content {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  height: 100%;
  box-sizing: border-box;
  padding: 0 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-center {
  min-width: 0;
  flex: 1;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-shrink: 0;
}

@media (max-width: 760px) {
  .header-content {
    gap: 8px;
    padding: 0 10px;
  }

  .header-left {
    display: none;
  }

  .header-center {
    justify-content: flex-start;
    gap: 12px;
    overflow: hidden;
  }

  .header-right {
    gap: 8px;
  }
}

/* 占满 header 以下区域；长页面（首页等）在 el-main 内滚动，勿在 main-content 上 hidden 裁切 */
.el-main {
  background-color: #f5f7fa;
  padding: 0;
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1 1 0;
  min-height: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
}
</style>
