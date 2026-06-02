import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    component: () => import("../views/main/HomeFrame.vue"),
    children: [
      {
        path: "", 
        name: "homeframe",
        redirect: "/home", 
      },
      {
        path: "/login",
        name: "login",
        component: () => import("../views/auth/Login.vue"),
      },
      {
        path: "/home",
        name: "home",
        component: () => import("../views/public/Home.vue"),
      },
      {
        path: "/register",
        name: "register",
        component: () => import("../views/auth/Register.vue"),
      },
      {
        path: "/resetpwd",
        name: "resetpwd",
        component: () => import("../views/auth/ResetPwd.vue"),
      },
      {
        path: "/valuation",
        name: "valuation",
        component: () => import("../views/public/Valuation.vue"),
        meta: { title: "AI 智能估价", requiresAuth: true }
      },
      {
        path: "/market",
        name: "market",
        component: () => import("../views/public/Market.vue"),
        meta: { title: "交易广场" }
      },
      {
        path: "/goods/:id",
        name: "GoodsDetail",
        component: () => import("../views/goods/GoodsDetail.vue"),
        meta: { title: "商品详情" }
      },
      {
        path: "/orders",
        name: "orders",
        component: () => import("../views/main/OrdersFrame.vue"),
        redirect: "/orders/bought",
        children: [
          {
            path: "publish",
            name: "Publish",
            component: () => import("../views/orders/Publish.vue"),
            meta: { title: "发布商品", requiresAuth: true }
          },
          {
            path: "published",
            name: "MyPublished",
            component: () => import("../views/orders/MyPublished.vue"),
            meta: { title: "我发布的", requiresAuth: true }
          },
          {
            path: "sold",
            name: "orders-sold",
            component: () => import("../views/orders/MySold.vue"),
            meta: { title: "我卖出的", requiresAuth: true },
          },
          {
            path: "bought",
            name: "orders-bought",
            component: () => import("../views/orders/MyBought.vue"),
            meta: { title: "我买到的", requiresAuth: true },
          },
          {
            path: "favorites",
            name: "orders-favorites",
            component: () => import("../views/orders/MyLikes.vue"),
            meta: { title: "我的收藏", requiresAuth: true }
          },
          {
            path: "profile",
            name: "orders-profile",
            component: () => import("../views/user/Profile.vue"),
            meta: { title: "个人资料", requiresAuth: true },
          },
          {
            path: "messages",
            name: "orders-messages",
            component: () => import("../views/chat/ChatList.vue"),
            meta: { title: "我的消息", requiresAuth: true },
          },
          {
            path: "address",
            name: "orders-address",
            component: () => import("../views/user/Address.vue"),
            meta: { title: "地址管理", requiresAuth: true },
          },
          {
            path: "security",
            name: "orders-security",
            component: () => import("../views/user/Security.vue"),
            meta: { title: "账号与安全", requiresAuth: true },
          },
          {
            path: "wallet",
            name: "orders-wallet",
            component: () => import("../views/user/Wallet.vue"),
            meta: { title: "资产钱包", requiresAuth: true },
          },
        ],
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem("access");
  const authPages = ["login", "register", "resetpwd"];
  if (authPages.includes(to.name as string) && token) {
    next({ name: "home" });
    return;
  }

  if (to.matched.some(record => record.meta.requiresAuth) && !token) {
    next({ name: "login" });
    return;
  }
  next();
});

export default router;
