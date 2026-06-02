<template>
  <AuthLayout>
    <div class="form-wrapper">
      <h2 class="welcome-text">欢迎登录</h2>
      <p class="welcome-sub">二手3C智能估价交易平台</p>

      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="login-form" size="large">
        <el-form-item prop="email">
          <el-input v-model="loginForm.email" placeholder="请输入邮箱地址" :prefix-icon="Message" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" show-password />
        </el-form-item>

        <div class="form-options">
          <el-checkbox v-model="loginForm.rememberMe">记住我</el-checkbox>
          <el-link type="primary" underline="never" @click="router.push('/resetpwd')">忘记密码？</el-link></div>

        <el-form-item>
          <el-button type="primary" class="login-btn" :loading="loading" @click="handleLogin">立即登录</el-button>
        </el-form-item>

        <div class="register-guide">
          还没有账号？<el-link type="primary" underline="never" @click="router.push('/register')">立即注册</el-link>
        </div>
      </el-form>
    </div>
  </AuthLayout>
</template>

<script lang="ts" setup name="login2">
import AuthLayout from "@/components/AuthLayout.vue"; 
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { Message, Lock } from "@element-plus/icons-vue";
import type { FormInstance, FormRules } from "element-plus";
import { ElMessage } from "element-plus";
import authAPI from "@/api/authapi";
import { useUserStore } from "@/store/userstore";
import {emailRules,passwordRules} from "@/utils/rules"
import { useVcode } from '@/composables/useVcode'

const router = useRouter();
const userStore = useUserStore();
const { verify } = useVcode()
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

// 登录表单规则 utils/rules.ts
const loginRules = reactive<FormRules>({
  email: emailRules,
  password: passwordRules,
});

// 组件挂载时检查是否记住密码
onMounted(() => {
  const remembered = localStorage.getItem('rememberMe');
  if (remembered) {
    try {
      const { email, password } = JSON.parse(remembered);
      loginForm.email = email;
      // 简单base64解码
      loginForm.password = atob(password);
      loginForm.rememberMe = true;
    } catch (e) {
      localStorage.removeItem('rememberMe');
    }
  }
});

// 核心登录点击事件
const handleLogin = async () => {
  if (!loginFormRef.value) return;
  // 校验表单
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      // 触发全局验证
      const isVerified = await verify()
      if (!isVerified) {
        ElMessage.warning('验证未通过，无法登录')
        return
      }

      loading.value = true;
      try {
        const res = await authAPI.loginAPI({
          email: loginForm.email,
          password: loginForm.password,
        });

        if (res.code === 200) {
          ElMessage.success("登录成功！");
          const userInfo = res.data.user_info as any
          // 更新状态
          userStore.setLoginState(
            res.data.access, 
            res.data.refresh, 
            userInfo.nickname || userInfo.username || 'User',
            userInfo.avatar || '', // 传递头像
            userInfo.id // 传递用户ID
          );
          
          // 处理记住我
          if (loginForm.rememberMe) {
            localStorage.setItem('rememberMe', JSON.stringify({
              email: loginForm.email,
              password: btoa(loginForm.password) // 简单base64编码
            }));
          } else {
            localStorage.removeItem('rememberMe');
          }

          router.push("/");
        } else {
        }
      } catch (error) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    }
  });
};

</script>

<style scoped>
.form-wrapper { width: 100%; max-width: 380px; }
.welcome-text { font-size: 28px; color: #1e293b; margin-bottom: 8px; font-weight: 700; }
.welcome-sub { font-size: 15px; color: #64748b; margin-bottom: 40px; }
.login-form :deep(.el-input__wrapper) { background-color: #f8fafc; box-shadow: none; border: 1px solid #e2e8f0; transition: all 0.3s ease; padding: 10px 15px; border-radius: 10px; }
.login-form :deep(.el-input__wrapper.is-focus) { background-color: #fff; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15); }
.login-form :deep(.el-input__inner) { height: 44px; font-size: 15px; }
.login-form :deep(.el-checkbox__input.is-checked .el-checkbox__inner) { background-color: #3b82f6; border-color: #3b82f6; }
.login-form :deep(.el-checkbox__label) { color: #64748b; }
.form-options { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.login-btn { width: 100%; height: 52px; font-size: 16px; font-weight: 600; border-radius: 10px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); border: none; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2); transition: all 0.2s ease; }
.login-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3); }
.login-btn:active { transform: translateY(0); }
.register-guide { text-align: center; margin-top: 24px; color: #64748b; font-size: 14px; }
.register-guide .el-link { vertical-align: baseline; margin-left: 5px; font-weight: 600; font-size: 14px; }
</style>
