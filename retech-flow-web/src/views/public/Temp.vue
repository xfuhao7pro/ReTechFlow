<template>
  <div class="login-page">

    <!-- 背景装饰 -->
    <div class="bg-deco">
      <div class="deco-circle c1" />
      <div class="deco-circle c2" />
      <div class="deco-circle c3" />
      <div class="deco-wave" />
    </div>

    <div class="login-box">

      <!-- ══════════════════════════════
           左侧
      ══════════════════════════════ -->
      <div class="login-left">

        <!-- Logo 区域：比例 2044:336 ≈ 6:1，建议显示宽度 240px，高度约 39px -->
        <div class="logo-area">
          <img src="@/assets/icon.png" alt="平台Logo" class="brand-logo-img" />
        </div>

        <!-- 标语 -->
        <div class="left-headline">
          <h2>卖得更贵</h2>
          <h2>买得更值</h2>
          <h2 class="headline-accent">AI 给你一个公道价</h2>
        </div>

        <p class="left-desc">
          不再被压价，不再买亏。<br />
          每日扫描百万条成交数据，给你最真实的市场参考价。
        </p>

        <!-- 卖点标签 -->
        <div class="feature-tags">
          <div class="f-tag">
            <span class="f-tag-icon">🤖</span>
            <div>
              <div class="f-tag-title">AI 实时估价</div>
              <div class="f-tag-desc">误差率低于 3%</div>
            </div>
          </div>
          <div class="f-tag">
            <span class="f-tag-icon">🔒</span>
            <div>
              <div class="f-tag-title">担保安全交易</div>
              <div class="f-tag-desc">确认收货后才放款</div>
            </div>
          </div>
          <div class="f-tag">
            <span class="f-tag-icon">📊</span>
            <div>
              <div class="f-tag-title">行情趋势分析</div>
              <div class="f-tag-desc">掌握最佳出售时机</div>
            </div>
          </div>
        </div>

        <!-- 底部数据统计 -->
        <div class="left-stats">
          <div class="stat-item">
            <span class="stat-num">128万+</span>
            <span class="stat-label">注册用户</span>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <span class="stat-num">99.6%</span>
            <span class="stat-label">估价准确率</span>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <span class="stat-num">86万+</span>
            <span class="stat-label">累计成交</span>
          </div>
        </div>

      </div>

      <!-- ══════════════════════════════
           右侧：登录表单
      ══════════════════════════════ -->
      <div class="login-right">
        <div class="form-wrapper">

          <h2 class="welcome-text">欢迎登录</h2>
          <p class="welcome-sub">3C 智能估价交易平台</p>

          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            size="large"
          >
            <el-form-item prop="email">
              <el-input
                v-model="loginForm.email"
                placeholder="请输入邮箱地址"
                :prefix-icon="Message"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="loginForm.rememberMe">记住我</el-checkbox>
              <el-link type="primary" :underline="false">忘记密码？</el-link>
            </div>

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
          </el-form>

          <div class="register-guide">
            还没有账号？
            <el-link type="primary" :underline="false" @click="goToRegister">
              立即注册
            </el-link>
          </div>

          <!-- 信任标识 -->
          <div class="trust-row">
            <span class="trust-item"><span class="trust-check">✓</span> 数据加密传输</span>
            <span class="trust-item"><span class="trust-check">✓</span> 平台担保交易</span>
            <span class="trust-item"><span class="trust-check">✓</span> 7天无忧退款</span>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup name="login">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Message, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import authApi from '@/api/authapi'
import { useUserStore } from '@/store/userstore'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({ email: '', password: '', rememberMe: false })

const loginRules = reactive<FormRules>({
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度不能少于6位或大于20位', trigger: 'blur' },
  ],
})

const handleLogin = async () => {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await authApi.loginAPI({
          email: loginForm.email,
          password: loginForm.password,
        })
        if (res.code === 200) {
          ElMessage.success('登录成功！')
          const userInfo = res.data.user_info as any
          userStore.setLoginState(
            res.data.access,
            res.data.refresh,
            userInfo.nickname || userInfo.username || 'User'
          )
          router.push('/')
        } else {
          ElMessage.error(res.msg || '登录失败')
        }
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }
  })
}

const goToRegister = () => router.push('/register')
</script>

<style scoped>
/* ── 页面背景 ── */
.login-page {
  width: 100%;
  height: 100%;
  min-height: calc(100vh - 80px - 60px);
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #e8f4fd 0%, #f0f7ff 45%, #ddeeff 100%);
  position: relative;
  overflow: hidden;
}

/* ── 背景装饰 ── */
.bg-deco { position: absolute; inset: 0; pointer-events: none; }

.deco-circle { position: absolute; border-radius: 50%; }
.c1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(14,165,233,0.12) 0%, transparent 70%);
  top: -160px; left: -120px;
}
.c2 {
  width: 380px; height: 380px;
  background: radial-gradient(circle, rgba(59,130,246,0.1) 0%, transparent 70%);
  bottom: -100px; right: -80px;
}
.c3 {
  width: 220px; height: 220px;
  background: radial-gradient(circle, rgba(14,165,233,0.07) 0%, transparent 70%);
  top: 50%; left: 42%;
}
.deco-wave {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 130px;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 130'%3E%3Cpath fill='rgba(14,165,233,0.07)' d='M0,70 C240,110 480,20 720,70 C960,120 1200,30 1440,70 L1440,130 L0,130 Z'/%3E%3C/svg%3E") no-repeat bottom;
  background-size: cover;
}

/* ── 主卡片 ── */
.login-box {
  position: relative;
  z-index: 1;
  width: 1000px;
  min-height: 600px;
  display: flex;
  border-radius: 20px;
  box-shadow:
    0 20px 60px rgba(14, 165, 233, 0.13),
    0 4px 20px rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.65);
  overflow: hidden;
  margin: 40px 0;
}

/* ══ 左侧 ══ */
.login-left {
  flex: 1;
  background: linear-gradient(160deg, #0ea5e9 0%, #2563eb 100%);
  color: white;
  padding: 44px 40px 32px 40px;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* 左侧内部装饰圆 */
.login-left::before {
  content: '';
  position: absolute;
  width: 300px; height: 300px;
  border-radius: 50%;
  background: rgba(255,255,255,0.07);
  top: -80px; right: -60px;
  pointer-events: none;
}
.login-left::after {
  content: '';
  position: absolute;
  width: 180px; height: 180px;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
  bottom: 60px; left: -40px;
  pointer-events: none;
}

/* Logo 区域
   原始尺寸 2044×336，约 6:1 宽高比
   设定显示宽度 240px → 高度自动约 39px */
.logo-area {
  position: relative;
  z-index: 1;
  margin-bottom: 32px;
}
.brand-logo-img {
  display: block;
  width: 240px;
  height: auto;      /* 按比例：240 / 6.08 ≈ 39px */
  object-fit: contain;
  /* 若 logo 原色在蓝色背景上不清晰，取消下行注释让 logo 变白 */
  /* filter: brightness(0) invert(1); */
}

/* 标语 */
.left-headline {
  position: relative;
  z-index: 1;
  margin-bottom: 14px;
}
.left-headline h2 {
  font-size: 30px;
  font-weight: 800;
  line-height: 1.35;
  color: #fff;
}
.headline-accent {
  color: #bfdbfe !important;
  font-size: 24px !important;
}

.left-desc {
  position: relative;
  z-index: 1;
  font-size: 13.5px;
  color: rgba(255,255,255,0.78);
  line-height: 1.9;
  margin-bottom: 24px;
}

/* 卖点标签 */
.feature-tags {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 28px;
  flex: 1;
}
.f-tag {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255,255,255,0.13);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 12px;
  padding: 11px 14px;
  transition: background 0.2s;
}
.f-tag:hover { background: rgba(255,255,255,0.2); }
.f-tag-icon { font-size: 22px; flex-shrink: 0; }
.f-tag-title { font-size: 13px; font-weight: 600; color: #fff; margin-bottom: 2px; }
.f-tag-desc { font-size: 11px; color: rgba(255,255,255,0.65); }

/* 底部统计 */
.left-stats {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 0;
  padding-top: 18px;
  border-top: 1px solid rgba(255,255,255,0.18);
}
.stat-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
  text-align: center;
}
.stat-num { font-size: 17px; font-weight: 800; color: #fff; }
.stat-label { font-size: 10px; color: rgba(255,255,255,0.6); letter-spacing: 0.5px; }
.stat-divider {
  width: 1px; height: 32px;
  background: rgba(255,255,255,0.2);
  flex-shrink: 0;
}

/* ══ 右侧 ══ */
.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 52px;
  background-color: rgba(255, 255, 255, 0.45);
}

.form-wrapper { width: 100%; max-width: 340px; }

.welcome-text {
  font-size: 28px;
  color: #1e293b;
  margin-bottom: 6px;
  font-weight: 700;
}
.welcome-sub {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 32px;
}

/* 输入框 */
.login-form :deep(.el-input__wrapper) {
  background-color: #f1f5f9;
  box-shadow: none;
  border: 1.5px solid transparent;
  transition: all 0.25s ease;
  padding: 8px 15px;
  border-radius: 10px;
}
.login-form :deep(.el-input__wrapper:hover) {
  border-color: #bae6fd;
  background-color: #f8fbff;
}
.login-form :deep(.el-input__wrapper.is-focus) {
  background-color: #fff;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.12);
}
.login-form :deep(.el-input__inner) {
  height: 40px;
  color: #1e293b;
}
.login-form :deep(.el-form-item) { margin-bottom: 18px; }

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 10px !important;
  background: linear-gradient(90deg, #0ea5e9 0%, #3b82f6 100%) !important;
  border: none !important;
  margin-top: 6px;
  letter-spacing: 1px;
  box-shadow: 0 4px 14px rgba(14, 165, 233, 0.3) !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
.login-btn:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.42) !important;
}
.login-btn:active { transform: translateY(0) !important; }

.register-guide {
  text-align: center;
  margin-top: 20px;
  margin-bottom: 24px;
  color: #64748b;
  font-size: 14px;
}
.register-guide .el-link {
  vertical-align: baseline;
  margin-left: 4px;
  font-weight: 600;
}

/* 信任标识 */
.trust-row {
  display: flex;
  justify-content: center;
  gap: 14px;
  flex-wrap: wrap;
  padding-top: 18px;
  border-top: 1px solid #f1f5f9;
}
.trust-item {
  font-size: 11px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 4px;
}
.trust-check { color: #0ea5e9; font-weight: 700; }
</style>