<template>
  <div class="admin-shell">
    <aside class="admin-aside">
      <div class="aside-brand">
        <div class="brand-logo">R</div>
        <div>
          <strong>ReTechFlow</strong>
          <span>{{ roleText }}</span>
        </div>
      </div>

      <el-menu :default-active="route.path" router class="admin-menu">
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>数据大屏</span>
        </el-menu-item>
        <el-menu-item index="/admin/goods">
          <el-icon><Goods /></el-icon>
          <span>商品审核</span>
        </el-menu-item>
        <el-menu-item index="/admin/identity">
          <el-icon><Postcard /></el-icon>
          <span>实名认证审核</span>
        </el-menu-item>
        <el-menu-item index="/admin/orders">
          <el-icon><Tickets /></el-icon>
          <span>订单监管</span>
        </el-menu-item>
        <el-menu-item index="/admin/categories">
          <el-icon><Grid /></el-icon>
          <span>机型分类库</span>
        </el-menu-item>
        <el-menu-item index="/admin/announcements">
          <el-icon><Bell /></el-icon>
          <span>公告管理</span>
        </el-menu-item>
        <el-menu-item v-if="isSuperAdmin" index="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </aside>

    <main class="admin-main">
      <header class="admin-topbar">
        <div>
          <h2>{{ route.meta.title || '后台管理' }}</h2>
          <p>平台审核、交易监管、用户治理与运营配置</p>
        </div>
        <div class="topbar-user">
          <el-avatar :size="34" :src="getImageUrl(userStore.userAvatar)" />
          <span>{{ userStore.userName }}</span>
          <el-button link type="primary" @click="logout">退出</el-button>
        </div>
      </header>

      <section class="admin-content">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bell, DataBoard, Goods, Grid, Postcard, Tickets, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/userstore'
import { getImageUrl } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isSuperAdmin = computed(() => Number(userStore.userRole) === 3)
const roleText = computed(() => (isSuperAdmin.value ? '系统管理员' : '平台审核员'))

const logout = () => {
  userStore.logout()
  router.replace('/admin/login')
}
</script>

<style scoped>
.admin-shell {
  display: grid;
  grid-template-columns: 236px minmax(0, 1fr);
  min-height: 100vh;
  background: #f5f8fb;
}

.admin-aside {
  background: #ffffff;
  border-right: 1px solid #e3eaf3;
}

.aside-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 72px;
  padding: 0 20px;
  border-bottom: 1px solid #edf2f7;
}

.brand-logo {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 8px;
  background: #1f5eae;
  color: #fff;
  font-weight: 800;
}

.aside-brand strong,
.aside-brand span {
  display: block;
}

.aside-brand strong {
  color: #172033;
}

.aside-brand span {
  margin-top: 3px;
  color: #64748b;
  font-size: 12px;
}

.admin-menu {
  border-right: 0;
  padding: 12px;
}

.admin-menu :deep(.el-menu-item) {
  height: 42px;
  margin-bottom: 6px;
  border-radius: 8px;
}

.admin-menu :deep(.el-menu-item.is-active) {
  background: #eff6ff;
  color: #1d5fb8;
  font-weight: 700;
}

.admin-main {
  min-width: 0;
}

.admin-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
  padding: 0 28px;
  background: #ffffff;
  border-bottom: 1px solid #e3eaf3;
}

.admin-topbar h2 {
  margin: 0 0 4px;
  color: #172033;
  font-size: 20px;
}

.admin-topbar p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.topbar-user {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #334155;
  font-size: 14px;
}

.admin-content {
  padding: 24px 28px;
}

.admin-shell :deep(*) {
  transition: none !important;
  animation: none !important;
}

.admin-shell :deep(.el-tag),
.admin-shell :deep(.el-tag *),
.admin-shell :deep(.el-button),
.admin-shell :deep(.el-button *),
.admin-shell :deep(.el-table__row),
.admin-shell :deep(.el-table__cell),
.admin-shell :deep(.el-menu-item),
.admin-shell :deep(.el-select__wrapper) {
  transform: none !important;
}

@media (max-width: 860px) {
  .admin-shell {
    grid-template-columns: 1fr;
  }

  .admin-aside {
    position: static;
  }
}
</style>
