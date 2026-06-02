<template>
  <div class="orders-frame">
    <el-container class="orders-inner">
      <el-aside width="248px" class="orders-aside">
        <div class="aside-title">
          <el-icon class="aside-title-icon"><UserFilled /></el-icon>
          <span>个人中心</span>
        </div>
        <el-menu
          :default-active="activePath"
          :default-openeds="defaultOpeneds"
          class="orders-menu"
          router
          :collapse-transition="false"
        >
          <el-menu-item index="/orders/publish">
            <el-icon><Edit /></el-icon>
            <span>发布商品</span>
          </el-menu-item>

          <el-sub-menu index="trade">
            <template #title>
              <el-icon><ShoppingCart /></el-icon>
              <span class="submenu-title">我的交易</span>
            </template>
            <el-menu-item index="/orders/bought">
              <el-icon><ShoppingBag /></el-icon>
              <span>我买到的</span>
            </el-menu-item>
            <el-menu-item index="/orders/sold">
              <el-icon><Goods /></el-icon>
              <span>我卖出的</span>
            </el-menu-item>
            <el-menu-item index="/orders/published">
              <el-icon><DocumentAdd /></el-icon>
              <span>我发布的</span>
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/orders/favorites">
            <el-icon><Star /></el-icon>
            <span>我的收藏</span>
          </el-menu-item>

          <el-menu-item index="/orders/messages">
            <el-icon><ChatDotRound /></el-icon>
            <span>我的消息</span>
          </el-menu-item>

          <el-sub-menu index="account">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span class="submenu-title">账户设置</span>
            </template>
            <el-menu-item index="/orders/profile">
              <el-icon><User /></el-icon>
              <span>个人资料</span>
            </el-menu-item>
            <el-menu-item index="/orders/address">
              <el-icon><Location /></el-icon>
              <span>地址管理</span>
            </el-menu-item>
            <el-menu-item index="/orders/security">
              <el-icon><Lock /></el-icon>
              <span>账号与安全</span>
            </el-menu-item>
            <el-menu-item index="/orders/wallet">
              <el-icon><Wallet /></el-icon>
              <span>资产钱包</span>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <el-main class="orders-main">
        <div class="orders-main-panel">
          <router-view v-slot="{ Component }">
            <keep-alive include="Publish">
              <component :is="Component" />
            </keep-alive>
          </router-view>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'OrdersFrame' })

import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  UserFilled,
  ShoppingCart,
  DocumentAdd,
  Goods,
  ShoppingBag,
  Star,
  Setting,
  User,
  Lock,
  Wallet,
  Edit,
  Location,
  ChatDotRound
} from '@element-plus/icons-vue'

const route = useRoute()

const activePath = computed(() => route.path)

const defaultOpeneds = computed(() => {
  const p = route.path
  const open: string[] = []
  if (
    p.startsWith('/orders/published') ||
    p.startsWith('/orders/sold') ||
    p.startsWith('/orders/bought')
  ) {
    open.push('trade')
  }
  if (
    p.startsWith('/orders/profile') ||
    p.startsWith('/orders/address') ||
    p.startsWith('/orders/security') ||
    p.startsWith('/orders/wallet')
  ) {
    open.push('account')
  }
  return open
})
</script>

<style scoped>
.orders-frame {
  /* 固定占满视口减去顶栏高度，不允许无限向下延伸 */
  height: calc(100vh - 80px);
  max-height: calc(100vh - 80px);
  padding: 20px 24px 28px;
  box-sizing: border-box;
  overflow: hidden;
}

.orders-inner {
  max-width: 1280px;
  margin: 0 auto;
  align-items: stretch;
  gap: 0;
  height: 100%;
}

.orders-aside {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  border: 1px solid rgba(64, 158, 255, 0.12);
  box-shadow:
    0 4px 24px rgba(31, 49, 85, 0.08),
    0 0 0 1px rgba(255, 255, 255, 0.8) inset;
  overflow: hidden;
  margin-right: 20px;
  flex-shrink: 0;
  align-self: flex-start;
  position: sticky;
  top: 0;
  max-height: 100%;
  overflow-y: auto;
}

.aside-title {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 18px 14px;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f47;
  letter-spacing: 0.03em;
  background: linear-gradient(
    118deg,
    rgba(64, 158, 255, 0.1) 0%,
    rgba(138, 101, 255, 0.08) 100%
  );
  border-bottom: 1px solid rgba(64, 158, 255, 0.14);
}

.aside-title-icon {
  font-size: 22px;
  color: #409eff;
}

.orders-menu {
  border-right: none;
  padding: 10px 8px 18px;
  background: transparent;
  --el-menu-item-height: 46px;
}

.orders-menu :deep(.el-menu-item),
.orders-menu :deep(.el-sub-menu__title) {
  border-radius: 8px;
  margin: 2px 0;
  color: #606266;
  transition:
    background 0.2s ease,
    color 0.2s ease;
}

.orders-menu :deep(.el-menu-item .el-icon),
.orders-menu :deep(.el-sub-menu__title .el-icon) {
  font-size: 18px;
  margin-right: 2px;
  color: #909399;
  transition: color 0.2s ease;
}

.orders-menu :deep(.el-menu-item:hover),
.orders-menu :deep(.el-sub-menu__title:hover) {
  background-color: rgba(64, 158, 255, 0.08) !important;
  color: #303133;
}

.orders-menu :deep(.el-menu-item:hover .el-icon),
.orders-menu :deep(.el-sub-menu__title:hover .el-icon) {
  color: #409eff;
}

.orders-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(
    90deg,
    rgba(64, 158, 255, 0.16) 0%,
    rgba(64, 158, 255, 0.06) 100%
  ) !important;
  color: #409eff !important;
  font-weight: 600;
  box-shadow: 0 1px 0 rgba(64, 158, 255, 0.12);
}

.orders-menu :deep(.el-menu-item.is-active .el-icon) {
  color: #409eff;
}

.orders-menu :deep(.el-sub-menu .el-menu-item) {
  min-width: auto;
  padding-left: 44px !important;
}

.orders-menu :deep(.el-sub-menu.is-opened > .el-sub-menu__title .el-icon) {
  color: #409eff;
}

.submenu-title {
  font-weight: 500;
}

.orders-main {
  padding: 0;
  overflow: hidden;
  background: transparent;
  flex: 1;
  min-width: 0;
}

.orders-main-panel {
  height: 100%;
  border-radius: 12px;
  border: 1px solid rgba(64, 158, 255, 0.1);
  box-shadow:
    0 4px 24px rgba(31, 49, 85, 0.07),
    0 0 0 1px rgba(255, 255, 255, 0.9) inset;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 子路由页面撑满面板（滚动由 DecorativeBackground 的 content-wrapper 管理） */
.orders-main-panel > :deep(*) {
  flex: 1;
  min-height: 0;
}
</style>
