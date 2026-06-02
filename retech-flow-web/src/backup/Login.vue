<template>
  <div class="login-page">
    <div class="login-box">
      <!-- 左侧login-form -->
      <div class="login-left">
        <div class="brand-info">
          <div class="brand-logo">
            <el-image
              class="brand-logo-img"
              :src="logo"
              fit="contain"
              alt="Logo"
            />
          </div>
          <div class="brand-slogan-container">
            <h2 class="brand-slogan">
              <span>拍照</span> · 
              <span>描述</span> · 
              <span>成交</span>
            </h2>
            <div class="slogan-decoration"></div>
          </div>
          <p class="brand-desc">
            <span class="ai-tag">AI</span> 全程代劳，成为您的私人质检师和定价师
          </p>
        </div>
        <!-- 装饰背景图标 -->
        <el-icon class="decoration-icon icon-monitor"><Monitor /></el-icon>
        <el-icon class="decoration-icon icon-camera"><Camera /></el-icon>
        <el-icon class="decoration-icon icon-phone"><Iphone /></el-icon>
      </div>

      <!-- 登录表单 -->
      <div class="login-right">
        <div class="form-wrapper">
          <h2 class="welcome-text">欢迎登录</h2>
          <p class="welcome-sub">二手3C智能估价交易平台</p>

          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            size="large"
          >
            <!-- 邮箱输入框 -->
            <el-form-item prop="email">
              <el-input
                v-model="loginForm.email"
                placeholder="请输入邮箱地址"
                :prefix-icon="Message"
              />
            </el-form-item>

            <!-- 密码输入框 -->
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <!-- 记住我/忘记密码 -->
            <div class="form-options">
              <el-checkbox v-model="loginForm.rememberMe">记住我</el-checkbox>
              <el-link type="primary" :underline="false">忘记密码？</el-link>
            </div>

            <!-- 登录按钮 -->
            <el-form-item>
              <el-button
                type="primary"
                class="login-btn"
                :loading="loading"
                @click="handleLogin"
              >
                立即登录
              </el-button>
            </el-form-item>

            <!-- 注册引导 -->
            <div class="register-guide">
              还没有账号？
              <el-link type="primary" :underline="false" @click="goToRegister">
                立即注册
              </el-link>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup name="login">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { Message, Lock, Monitor, Camera, Iphone } from "@element-plus/icons-vue";
import type { FormInstance, FormRules } from "element-plus";
import { ElMessage } from "element-plus";
import authApi from "@/api/authapi";
import { useUserStore } from "@/store/userstore";
import logo from '../../assets/icon.png'

const router = useRouter();
const userStore = useUserStore();
// 表单实例
const loginFormRef = ref<FormInstance>();
// 响应状态
const loading = ref(false);

// 登录表单对象
const loginForm = reactive({
  email: "",
  password: "",
  rememberMe: false,
});
// 登录表单规则
const loginRules = reactive<FormRules>({
  email: [
    { required: true, message: "请输入邮箱地址", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    {
      min: 6,
      max: 20,
      message: "密码长度不能少于6位或大于20位",
      trigger: "blur",
    },
  ],
});

// 核心登录点击事件
const handleLogin = async () => {
  if (!loginFormRef.value) return;
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const res = await authApi.loginAPI({
          email: loginForm.email,
          password: loginForm.password,
        });

        if (res.code === 200) {
          ElMessage.success("登录成功！");
          const userInfo = res.data.user_info as any
          userStore.setLoginState(res.data.access, res.data.refresh, userInfo.nickname || userInfo.username || 'User');
          router.push("/");
        }
      } catch (error) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    }
  });
};

//跳转注册页面
const goToRegister = () => {
  router.push("/register");
};
</script>

<style scoped>
/* 页面容器 */
.login-page {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8fafc;
}

/* 主登录框 */
.login-box {
  width: 888px;
  height: 550px;
  display: flex;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
  background: #ffffff;
  overflow: hidden;
  position: relative;
}

/* --- 左侧品牌区域 --- */
.login-left {
  width: 400px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.brand-info {
  position: relative;
  z-index: 2;
}

.brand-logo {
  margin-bottom: 70px;
}

.brand-logo-img {
  width: 366px;
  height: 50px;
}

.brand-slogan-container {
  margin-bottom: 30px;
}

.brand-slogan {
  font-size: 36px;
  line-height: 1.3;
  font-weight: 800;
  letter-spacing: 1px;
  color: #ffffff; /* 确保在深色背景上清晰可见 */
}

.slogan-decoration {
  width: 40px;
  height: 6px;
  background-color: #ffffff;
  border-radius: 3px;
  margin-top: 20px;
  opacity: 0.8;
}

.brand-desc {
  font-size: 18px;
  line-height: 1.6;
  opacity: 0.9;
  font-weight: 400;
  display: flex;
  align-items: center;
}

.ai-tag {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 1000;
  margin-right: 10px;
  font-size: 14px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 装饰背景图标 */
.decoration-icon {
  position: absolute;
  color: rgba(255, 255, 255, 0.1);
  pointer-events: none;
  z-index: 1;
}

.icon-monitor {
  font-size: 200px;
  top: -40px;
  right: -60px;
  transform: rotate(15deg);
}

.icon-camera {
  font-size: 120px;
  bottom: 80px;
  left: -30px;
  transform: rotate(-20deg);
}

.icon-phone {
  font-size: 100px;
  bottom: -20px;
  right: 20px;
  transform: rotate(30deg);
}

/* --- 右侧表单区域 --- */
.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 58px;
  background-color: #ffffff;
}

.form-wrapper {
  width: 100%;
  max-width: 380px;
}

.welcome-text {
  font-size: 28px;
  color: #1e293b;
  margin-bottom: 8px;
  font-weight: 700;
}

.welcome-sub {
  font-size: 15px;
  color: #64748b;
  margin-bottom: 40px;
}

/* Element Plus 样式覆盖 */
.login-form :deep(.el-input__wrapper) {
  background-color: #f8fafc;
  box-shadow: none;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  padding: 10px 15px;
  border-radius: 10px;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  background-color: #fff;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.login-form :deep(.el-input__inner) {
  height: 44px;
  font-size: 15px;
}

.login-form :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

.login-form :deep(.el-checkbox__label) {
  color: #64748b;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.login-btn {
  width: 100%;
  height: 52px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
  transition: all 0.2s ease;
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
}

.login-btn:active {
  transform: translateY(0);
}

.register-guide {
  text-align: center;
  margin-top: 24px;
  color: #64748b;
  font-size: 14px;
}

.register-guide .el-link {
  vertical-align: baseline;
  margin-left: 5px;
  font-weight: 600;
  font-size: 14px;
}
</style>