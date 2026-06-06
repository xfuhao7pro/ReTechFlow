import { createRouter, createWebHistory } from 'vue-router'
import { openAuthDialog } from '@/composables/useAuthDialog'

const routes = [
  {
    path: '/',
    component: () => import('../views/main/HomeFrame.vue'),
    children: [
      { path: '', redirect: '/home' },
      { path: '/home', name: 'home', component: () => import('../views/public/Home.vue') },
      { path: '/valuation', name: 'valuation', component: () => import('../views/public/Valuation.vue'), meta: { title: 'AI 智能估价' } },
      { path: '/market', name: 'market', component: () => import('../views/public/Market.vue'), meta: { title: '交易广场' } },
      { path: '/goods/:id', name: 'GoodsDetail', component: () => import('../views/goods/GoodsDetail.vue'), meta: { title: '商品详情' } },
      {
        path: '/orders',
        name: 'orders',
        component: () => import('../views/main/OrdersFrame.vue'),
        redirect: '/orders/bought',
        children: [
          { path: 'publish', name: 'Publish', component: () => import('../views/orders/Publish.vue'), meta: { title: '发布商品', requiresAuth: true } },
          { path: 'published', name: 'MyPublished', component: () => import('../views/orders/MyPublished.vue'), meta: { title: '我发布的', requiresAuth: true } },
          { path: 'sold', name: 'orders-sold', component: () => import('../views/orders/MySold.vue'), meta: { title: '我卖出的', requiresAuth: true } },
          { path: 'bought', name: 'orders-bought', component: () => import('../views/orders/MyBought.vue'), meta: { title: '我买到的', requiresAuth: true } },
          { path: 'favorites', name: 'orders-favorites', component: () => import('../views/orders/MyLikes.vue'), meta: { title: '我的收藏', requiresAuth: true } },
          { path: 'profile', name: 'orders-profile', component: () => import('../views/user/Profile.vue'), meta: { title: '个人资料', requiresAuth: true } },
          { path: 'messages', name: 'orders-messages', component: () => import('../views/chat/ChatList.vue'), meta: { title: '我的消息', requiresAuth: true } },
          { path: 'address', name: 'orders-address', component: () => import('../views/user/Address.vue'), meta: { title: '地址管理', requiresAuth: true } },
          { path: 'security', name: 'orders-security', component: () => import('../views/user/Security.vue'), meta: { title: '账号与安全', requiresAuth: true } },
          { path: 'wallet', name: 'orders-wallet', component: () => import('../views/user/Wallet.vue'), meta: { title: '资产钱包', requiresAuth: true } },
        ],
      },
    ],
  },
  {
    path: '/admin/login',
    name: 'admin-login',
    component: () => import('../views/admin/AdminLogin.vue'),
    meta: { title: '后台登录' },
  },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    redirect: '/admin/dashboard',
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: 'dashboard', name: 'admin-dashboard', component: () => import('../views/admin/AdminDashboard.vue'), meta: { title: '后台控制台', requiresAuth: true, requiresAdmin: true } },
      { path: 'goods', name: 'admin-goods', component: () => import('../views/admin/AdminGoods.vue'), meta: { title: '商品审核', requiresAuth: true, requiresAdmin: true } },
      { path: 'identity', name: 'admin-identity', component: () => import('../views/admin/AdminIdentity.vue'), meta: { title: '实名认证审核', requiresAuth: true, requiresAdmin: true } },
      { path: 'orders', name: 'admin-orders', component: () => import('../views/admin/AdminOrders.vue'), meta: { title: '订单监管', requiresAuth: true, requiresAdmin: true } },
      { path: 'appeals', name: 'admin-appeals', component: () => import('../views/admin/AdminAppeals.vue'), meta: { title: '申诉仲裁', requiresAuth: true, requiresAdmin: true } },
      { path: 'categories', name: 'admin-categories', component: () => import('../views/admin/AdminCategories.vue'), meta: { title: '机型分类库', requiresAuth: true, requiresAdmin: true } },
      { path: 'announcements', name: 'admin-announcements', component: () => import('../views/admin/AdminAnnouncements.vue'), meta: { title: '公告管理', requiresAuth: true, requiresAdmin: true } },
      { path: 'users', name: 'admin-users', component: () => import('../views/admin/AdminUsers.vue'), meta: { title: '用户管理', requiresAuth: true, requiresAdmin: true, requiresSuperAdmin: true } },
    ],
  },
  { path: '/login', redirect: '/home' },
  { path: '/register', redirect: '/home' },
  { path: '/resetpwd', redirect: '/home' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access')
  const role = Number(localStorage.getItem('userRole') || 0)
  if (to.matched.some((record) => record.meta.requiresAuth) && !token) {
    if (to.path.startsWith('/admin')) return '/admin/login'
    openAuthDialog('login')
    return false
  }
  if (to.matched.some((record) => record.meta.requiresAdmin) && ![2, 3].includes(role)) {
    return '/admin/login'
  }
  if (to.matched.some((record) => record.meta.requiresSuperAdmin) && role !== 3) {
    return '/admin/dashboard'
  }
  return true
})

export default router
