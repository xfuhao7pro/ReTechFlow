<template>
  <el-dialog
    v-model="visible"
    class="auth-dialog"
    width="790px"
    :close-on-click-modal="false"
    destroy-on-close
    align-center
  >
    <div class="auth-shell">
      <section class="brand-panel">
        <div class="brand-content">
          <img class="brand-logo" :src="logo" alt="ReTechFlow" />
          <div class="brand-slogan">
            <h2><span>拍照</span><b>·</b><span>描述</span><b>·</b><span>成交</span></h2>
            <div class="slogan-line"></div>
          </div>
          <p><strong>AI</strong> 全程代劳，成为您的私人质检师和定价师</p>
        </div>
        <el-icon class="decor-icon monitor"><Monitor /></el-icon>
        <el-icon class="decor-icon camera"><Camera /></el-icon>
        <el-icon class="decor-icon phone"><Iphone /></el-icon>
      </section>

      <section class="form-panel">
        <div class="form-inner">
          <header class="auth-header">
            <h2>{{ title }}</h2>
            <p>{{ subtitle }}</p>
          </header>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            :validate-on-rule-change="false"
            class="auth-form"
            size="large"
          >
            <el-form-item prop="email">
              <el-input v-model="form.email" placeholder="请输入邮箱地址" :prefix-icon="Message" />
            </el-form-item>

            <el-form-item v-if="mode !== 'login'" prop="auth_code">
              <el-input v-model="form.auth_code" placeholder="请输入验证码" :prefix-icon="Key">
                <template #suffix>
                  <el-button
                    link
                    type="primary"
                    :disabled="sendingCode || countdown > 0"
                    @click="sendCode"
                  >
                    {{ countdown > 0 ? `${countdown}s 后重试` : '获取验证码' }}
                  </el-button>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                :placeholder="mode === 'reset' ? '请输入新密码' : '请输入密码'"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <el-form-item v-if="mode !== 'login'" prop="password_confirm">
              <el-input
                v-model="form.password_confirm"
                type="password"
                placeholder="请再次输入密码"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <div v-if="mode === 'login'" class="form-options">
              <el-checkbox v-model="form.rememberMe">记住我</el-checkbox>
              <el-link type="primary" underline="never" @click="switchMode('reset')">忘记密码？</el-link>
            </div>

            <el-button class="submit-btn" type="primary" :loading="loading" @click="submit">
              {{ submitText }}
            </el-button>

            <div class="mode-switch">
              <template v-if="mode === 'login'">
                还没有账号？<el-link type="primary" underline="never" @click="switchMode('register')">立即注册</el-link>
              </template>
              <template v-else>
                已有账号？<el-link type="primary" underline="never" @click="switchMode('login')">立即登录</el-link>
              </template>
            </div>
          </el-form>
        </div>
      </section>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { Camera, Iphone, Key, Lock, Message, Monitor } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import logo from '@/assets/icon.png'
import authAPI from '@/api/authapi'
import { useUserStore } from '@/store/userstore'
import { authCodeRules, emailRules, passwordRules } from '@/utils/rules'
import { useVcode } from '@/composables/useVcode'
import { useAuthDialog, type AuthDialogMode } from '@/composables/useAuthDialog'

const userStore = useUserStore()
const { verify } = useVcode()
const { visible, mode, closeAuthDialog } = useAuthDialog()
const formRef = ref<FormInstance>()
const loading = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)
let timer: number | null = null

const form = reactive({
  email: '',
  auth_code: '',
  password: '',
  password_confirm: '',
  rememberMe: false,
})

const validatePasswordConfirm = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (!value) callback(new Error('请再次输入密码'))
  else if (value !== form.password) callback(new Error('两次输入的密码不一致'))
  else callback()
}

const rules = computed<FormRules>(() => ({
  email: emailRules,
  password: passwordRules,
  ...(mode.value === 'login'
    ? {}
    : {
        auth_code: authCodeRules,
        password_confirm: [{ validator: validatePasswordConfirm, trigger: 'blur' }],
      }),
}))

const title = computed(() => ({
  login: '欢迎登录',
  register: '创建账号',
  reset: '重置密码',
}[mode.value]))

const subtitle = computed(() => ({
  login: '二手 3C 智能估价交易平台',
  register: '填写以下信息完成注册',
  reset: '通过邮箱验证码设置新密码',
}[mode.value]))

const submitText = computed(() => ({
  login: '立即登录',
  register: '立即注册',
  reset: '重置密码',
}[mode.value]))

const resetForm = () => {
  form.auth_code = ''
  form.password = ''
  form.password_confirm = ''
  void nextTick(() => formRef.value?.clearValidate())
}

const switchMode = (nextMode: AuthDialogMode) => {
  mode.value = nextMode
  resetForm()
}

watch(visible, (isVisible) => {
  if (isVisible) {
    void nextTick(() => formRef.value?.clearValidate())
  }
})

const startCountdown = (seconds = 60) => {
  countdown.value = Math.max(Number(seconds) || 60, 1)
  if (timer) clearInterval(timer)
  timer = window.setInterval(() => {
    countdown.value--
    if (countdown.value <= 0 && timer) {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

const sendCode = async () => {
  try {
    await formRef.value?.validateField('email')
  } catch {
    return
  }

  const passed = await verify()
  if (!passed) return

  sendingCode.value = true
  try {
    const response = await authAPI.sendCodeAPI(form.email)
    if (response.code === 200) {
      ElMessage.success(response.msg || '验证码已发送，请查收')
      startCountdown(response.data?.cooldown || 60)
    }
  } catch (error: any) {
    const cooldown = error?.response?.data?.data?.cooldown
    if (cooldown) startCountdown(cooldown)
  } finally {
    sendingCode.value = false
  }
}

const submit = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  if (mode.value === 'login') {
    const passed = await verify()
    if (!passed) return
  }

  loading.value = true
  try {
    if (mode.value === 'login') {
      const response = await authAPI.loginAPI({ email: form.email, password: form.password })
      if (response.code === 200) {
        const user = response.data.user_info as any
        userStore.setLoginState(
          response.data.access,
          response.data.refresh,
          user.nickname || user.username || 'User',
          user.avatar || '',
          user.id,
          user.role || 0,
        )
        if (form.rememberMe) {
          localStorage.setItem('rememberMe', JSON.stringify({ email: form.email }))
        } else {
          localStorage.removeItem('rememberMe')
        }
        ElMessage.success('登录成功')
        closeAuthDialog()
      }
      return
    }

    if (mode.value === 'register') {
      const response = await authAPI.registerAPI({
        email: form.email,
        auth_code: form.auth_code,
        password: form.password,
        password_confirm: form.password_confirm,
      })
      if (response.code === 200) {
        ElMessage.success('注册成功，请登录')
        switchMode('login')
      }
      return
    }

    const response = await authAPI.resetPasswordAPI({
      email: form.email,
      auth_code: form.auth_code,
      password: form.password,
      password_confirm: form.password_confirm,
    })
    if (response.code === 200) {
      ElMessage.success('密码重置成功，请登录')
      switchMode('login')
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const remembered = localStorage.getItem('rememberMe')
  if (!remembered) return
  try {
    form.email = JSON.parse(remembered).email || ''
    form.rememberMe = !!form.email
  } catch {
    localStorage.removeItem('rememberMe')
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
:global(.auth-dialog) {
  max-width: calc(100vw - 32px);
  padding: 0 !important;
  overflow: hidden;
  border: 0;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 24px 70px rgba(30, 64, 175, 0.2);
}

:global(.auth-dialog .el-dialog__header) {
  padding: 0;
  margin: 0;
}

:global(.auth-dialog .el-dialog__headerbtn) {
  top: 14px;
  right: 14px;
  z-index: 5;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
}

:global(.auth-dialog .el-dialog__close) {
  color: #64748b;
  font-size: 18px;
}

:global(.auth-dialog .el-dialog__body) {
  padding: 0;
}

.auth-shell {
  display: grid;
  grid-template-columns: 338px minmax(0, 1fr);
  min-height: 500px;
}

.brand-panel {
  position: relative;
  display: flex;
  align-items: center;
  overflow: hidden;
  padding: 38px 32px;
  color: #fff;
  background:
    radial-gradient(circle at 78% 8%, rgba(148, 219, 255, 0.34), transparent 30%),
    linear-gradient(145deg, #1e4e91 0%, #2466bd 56%, #2d7cda 100%);
}

.brand-content {
  position: relative;
  z-index: 2;
}

.brand-logo {
  display: block;
  width: 270px;
  max-width: 100%;
  height: 44px;
  margin-bottom: 64px;
  object-fit: contain;
  object-position: left center;
}

.brand-slogan h2 {
  display: flex;
  gap: 8px;
  margin: 0;
  color: #fff;
  font-size: 29px;
  line-height: 1.3;
  font-weight: 800;
}

.brand-slogan b {
  opacity: 0.72;
}

.slogan-line {
  width: 38px;
  height: 4px;
  margin-top: 16px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.85);
}

.brand-content p {
  display: flex;
  align-items: center;
  margin: 24px 0 0;
  color: rgba(255, 255, 255, 0.92);
  font-size: 15px;
  line-height: 1.7;
}

.brand-content strong {
  margin-right: 10px;
  padding: 2px 7px;
  border: 1px solid rgba(255, 255, 255, 0.42);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.18);
  font-size: 13px;
}

.decor-icon {
  position: absolute;
  color: rgba(255, 255, 255, 0.11);
  pointer-events: none;
}

.monitor { top: -36px; right: -52px; font-size: 170px; transform: rotate(15deg); }
.camera { bottom: 62px; left: -24px; font-size: 102px; transform: rotate(-20deg); }
.phone { right: 18px; bottom: -20px; font-size: 88px; transform: rotate(30deg); }

.form-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 38px 44px;
  background: linear-gradient(180deg, #fff 0%, #fbfdff 100%);
}

.form-inner {
  width: 100%;
  max-width: 340px;
}

.auth-header {
  margin-bottom: 26px;
}

.auth-header h2 {
  margin: 0 0 8px;
  color: #1e293b;
  font-size: 25px;
  font-weight: 700;
}

.auth-header p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.auth-form :deep(.el-form-item) {
  margin-bottom: 19px;
}

.auth-form :deep(.el-input__wrapper) {
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  background: #f8fafc;
  box-shadow: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.auth-form :deep(.el-input__wrapper.is-focus) {
  border-color: #3b82f6;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.14);
}

.auth-form :deep(.el-input__inner) {
  height: 32px;
  font-size: 14px;
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 0 21px;
}

.submit-btn {
  width: 100%;
  height: 44px;
  border: 0;
  border-radius: 7px;
  background: linear-gradient(135deg, #3279d6 0%, #1f5eae 100%);
  box-shadow: 0 5px 12px rgba(30, 78, 145, 0.2);
  font-size: 15px;
  font-weight: 600;
}

.mode-switch {
  margin-top: 19px;
  color: #64748b;
  text-align: center;
  font-size: 14px;
}

.mode-switch .el-link {
  margin-left: 4px;
  vertical-align: baseline;
  font-weight: 600;
}

@media (max-width: 760px) {
  :global(.auth-dialog) {
    width: min(440px, calc(100vw - 24px)) !important;
  }

  .auth-shell {
    display: block;
    min-height: auto;
  }

  .brand-panel {
    min-height: 120px;
    padding: 22px 24px;
  }

  .brand-logo {
    width: 250px;
    height: 38px;
    margin-bottom: 16px;
  }

  .brand-slogan h2 {
    gap: 7px;
    font-size: 22px;
  }

  .slogan-line,
  .brand-content p {
    display: none;
  }

  .monitor { top: -52px; right: -46px; font-size: 150px; }
  .camera,
  .phone { display: none; }

  .form-panel {
    padding: 30px 24px 28px;
  }
}
</style>
