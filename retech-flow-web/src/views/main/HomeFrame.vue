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
              <router-link to="/login" class="auth-btn login">登录</router-link>
              <router-link to="/register" class="auth-btn register">注册</router-link>
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
              <div class="message-bell" @click="router.push('/orders/messages')">
                <el-badge :value="totalUnread" :hidden="totalUnread === 0" :max="99">
                  <el-icon :size="22"><Bell /></el-icon>
                </el-badge>
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
import chatApi from '@/api/chatapi'
import { ref, onUnmounted, watch } from 'vue'
import {
  User,
  ShoppingBag,
  Goods,
  Star,
  SwitchButton,
  ArrowDown,
  DocumentAdd,
  Bell
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const valuationStore = useValuationStore()
// 使用storeToRefs保持响应性
const { isLoggedIn, userName, userAvatar } = storeToRefs(userStore)

const totalUnread = ref(0)
let unreadTimer: number | null = null

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

watch(isLoggedIn, (newVal) => {
  // 先清除旧的定时器，防止重复创建
  if (unreadTimer) {
    clearInterval(unreadTimer)
    unreadTimer = null
  }
  if (newVal) {
    fetchUnreadCount()
    unreadTimer = window.setInterval(fetchUnreadCount, 30000)
    // 建立估价 WebSocket 连接（全局生命周期，登录即连）
    valuationStore.connectWS()
  } else {
    totalUnread.value = 0
    // 退出登录时断开估价 WS 并重置状态
    valuationStore.reset()
  }
}, { immediate: true })

onUnmounted(() => {
  if (unreadTimer) clearInterval(unreadTimer)
  valuationStore.closeWS()
})

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 获取安全的头像URL
const getSafeAvatarUrl = (avatarPath: string) => {
  if (!avatarPath) return defaultAvatar
  // 使用之前抽离的全局 getImageUrl 工具函数来处理后端返回的相对路径
  return getImageUrl(avatarPath)
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
  router.push('/login')
}
</script>

<style scoped>
.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-shrink: 0; /* 防止挤压折行 */
}

.message-bell {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #fff;
  transition: opacity 0.3s;
  padding: 5px;
}

.message-bell:hover {
  opacity: 0.8;
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
  display: flex;
  flex-direction: column;
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
  width: 1000px; /* 从 888px 加大以容纳新增的图标和长昵称 */
  margin: 0 auto;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-center {
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