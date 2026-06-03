<template>
  <div class="admin-login">
    <section class="login-panel">
      <div class="brand">
        <div class="brand-mark">R</div>
        <div>
          <h1>ReTechFlow 后台</h1>
          <p>审核员 / 系统管理员统一入口</p>
        </div>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" class="login-form" size="large">
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="后台账号邮箱" :prefix-icon="Message" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="登录密码" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-button class="login-btn" type="primary" :loading="loading" @click="submit">登录后台</el-button>
      </el-form>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Lock, Message } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import authAPI from '@/api/authapi'
import { useUserStore } from '@/store/userstore'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  email: '',
  password: '',
})

const rules: FormRules = {
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const submit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res = await authAPI.loginAPI(form)
    const user = res.data.user_info as any
    if (![2, 3].includes(Number(user.role))) {
      ElMessage.error('该账号没有后台访问权限')
      return
    }
    userStore.setLoginState(
      res.data.access,
      res.data.refresh,
      user.nickname || user.email || '管理员',
      user.avatar || '',
      user.id,
      Number(user.role || 0),
    )
    ElMessage.success('登录成功')
    router.replace('/admin')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at 20% 10%, rgba(59, 130, 246, 0.14), transparent 28%),
    linear-gradient(135deg, #f8fbff 0%, #edf4fb 100%);
}

.login-panel {
  width: min(420px, 100%);
  padding: 34px;
  border: 1px solid #dbe6f3;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.12);
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 30px;
}

.brand-mark {
  display: grid;
  width: 46px;
  height: 46px;
  place-items: center;
  border-radius: 8px;
  background: #1f5eae;
  color: #fff;
  font-size: 24px;
  font-weight: 800;
}

.brand h1 {
  margin: 0 0 5px;
  color: #172033;
  font-size: 22px;
}

.brand p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.login-btn {
  width: 100%;
  height: 44px;
  border-radius: 8px;
  font-weight: 700;
}
</style>
