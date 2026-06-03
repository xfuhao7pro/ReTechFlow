<template>
  <DecorativeBackground>
  <div class="security-container">
    <div class="security-header">
      <h2>账号与安全</h2>
      <p class="subtitle">管理您的账号安全设置，保护您的账户信息</p>
    </div>

    <el-card class="security-card" shadow="never" v-loading="loading">
      <div class="security-list">
        <!-- 邮箱 -->
        <div class="security-item">
          <div class="item-content">
            <div class="item-title">
              <el-icon class="icon"><Message /></el-icon>
              <span>绑定邮箱</span>
            </div>
            <div class="item-desc">{{ securityData.email || '未绑定' }}</div>
          </div>
          <div class="item-action">
            <el-tag type="success" class="static-status-tag" v-if="securityData.email">已绑定</el-tag>
          </div>
        </div>

        <el-divider />

        <!-- 手机号 -->
        <div class="security-item">
          <div class="item-content">
            <div class="item-title">
              <el-icon class="icon"><Iphone /></el-icon>
              <span>绑定手机</span>
            </div>
            <div class="item-desc">{{ maskedPhone }}</div>
          </div>
          <div class="item-action">
            <el-button type="primary" link @click="openPhoneDialog">
              {{ securityData.telephone ? '更换手机号' : '绑定手机号' }}
            </el-button>
          </div>
        </div>

        <el-divider />

        <!-- 实名认证 -->
        <div class="security-item">
          <div class="item-content">
            <div class="item-title">
              <el-icon class="icon"><Postcard /></el-icon>
              <span>实名认证</span>
            </div>
            <div class="item-desc">
              <template v-if="securityData.is_verified">
                <div class="realname-info">
                  <span>{{ maskedRealName }}</span>
                  <span>{{ maskedIdCard }}</span>
                </div>
              </template>
              <template v-else-if="securityData.verification_status === 1">
                实名认证资料已提交，等待平台审核
              </template>
              <template v-else-if="securityData.verification_status === 3">
                已驳回：{{ securityData.verification_reject_reason || '请重新提交认证资料' }}
              </template>
              <template v-else>
                完成实名认证，解锁更多平台功能
              </template>
            </div>
          </div>
          <div class="item-action">
            <el-tag type="success" class="static-status-tag" v-if="securityData.is_verified">已认证</el-tag>
            <el-tag type="warning" class="static-status-tag" v-else-if="securityData.verification_status === 1">审核中</el-tag>
            <el-button type="primary" v-else @click="openRealNameDialog">
              去认证
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 更换/绑定手机号弹窗 -->
    <el-dialog
      v-model="phoneDialogVisible"
      :title="securityData.telephone ? '更换手机号' : '绑定手机号'"
      width="400px"
      destroy-on-close
    >
      <el-form ref="phoneFormRef" :model="phoneForm" :rules="phoneRules" label-width="80px">
        <el-form-item label="新手机号" prop="telephone">
          <el-input v-model="phoneForm.telephone" placeholder="请输入新的手机号" maxlength="11" />
        </el-form-item>
        <el-form-item label="密码确认" prop="password">
          <el-input v-model="phoneForm.password" type="password" placeholder="请输入登录密码确认身份" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="phoneDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPhone" :loading="submittingPhone">确定</el-button>
      </template>
    </el-dialog>

    <!-- 实名认证弹窗 -->
    <el-dialog
      v-model="realNameDialogVisible"
      title="实名认证"
      width="400px"
      destroy-on-close
    >
      <el-alert
        title="实名认证信息一经提交不可修改，请确保填写您本人的真实信息。"
        type="info"
        show-icon
        :closable="false"
        style="margin-bottom: 20px"
      />
      <el-form ref="realNameFormRef" :model="realNameForm" :rules="realNameRules" label-width="80px">
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="realNameForm.real_name" placeholder="请输入您的真实姓名" />
        </el-form-item>
        <el-form-item label="身份证号" prop="id_card">
          <el-input v-model="realNameForm.id_card" placeholder="请输入您的身份证号" maxlength="18" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="realNameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRealName" :loading="submittingRealName">提交认证</el-button>
      </template>
    </el-dialog>
  </div>
  </DecorativeBackground>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Message, Iphone, Postcard } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import userAPI from '@/api/userapi'
import type { SecurityData } from '@/api/userapi'
import DecorativeBackground from '@/components/DecorativeBackground.vue'
import { useVcode } from '@/composables/useVcode'

const { verify } = useVcode()

const loading = ref(true)

const securityData = reactive<SecurityData>({
  email: '',
  telephone: '',
  real_name: '',
  id_card: '',
  is_verified: false,
  verification_status: 0,
  verification_reject_reason: ''
})

// 格式化脱敏手机号
const maskedPhone = computed(() => {
  const phone = securityData.telephone
  if (!phone) return '未绑定'
  if (phone.length === 11) {
    return phone.substring(0, 3) + '****' + phone.substring(7)
  }
  return phone
})

// 格式化脱敏姓名
const maskedRealName = computed(() => {
  const name = securityData.real_name
  if (!name) return ''
  if (name.length <= 2) {
    return name.substring(0, 1) + '*'
  }
  return name.substring(0, 1) + '*'.repeat(name.length - 2) + name.substring(name.length - 1)
})

// 格式化脱敏身份证
const maskedIdCard = computed(() => {
  const id = securityData.id_card
  if (!id) return ''
  if (id.length === 18) {
    return id.substring(0, 3) + '***********' + id.substring(14)
  }
  return id
})

const validateIdCard = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  const id = value.trim().toUpperCase()
  if (!/^\d{17}[\dX]$/.test(id)) {
    callback(new Error('请输入18位身份证号码'))
    return
  }
  const birthYear = Number(id.slice(6, 10))
  const birthMonth = Number(id.slice(10, 12))
  const birthDay = Number(id.slice(12, 14))
  const birthday = new Date(birthYear, birthMonth - 1, birthDay)
  const validDate = birthday.getFullYear() === birthYear
    && birthday.getMonth() === birthMonth - 1
    && birthday.getDate() === birthDay
  if (!validDate || birthday > new Date() || birthYear < 1900) {
    callback(new Error('身份证出生日期不正确'))
    return
  }
  const weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
  const checkCodes = '10X98765432'
  const sum = weights.reduce((total, weight, index) => total + Number(id[index]) * weight, 0)
  if (checkCodes[sum % 11] !== id[17]) {
    callback(new Error('身份证校验码不正确'))
    return
  }
  callback()
}

// 加载数据
const fetchSecurityData = async () => {
  loading.value = true
  try {
    const res = await userAPI.getSecurityAPI()
    if (res.code === 200 && res.data) {
      Object.assign(securityData, res.data)
    } else {
      ElMessage.error(res.msg || '获取安全设置失败')
    }
  } catch (error) {
    console.error('获取安全设置失败', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

// ============== 手机号绑定/更换 ==============
const phoneDialogVisible = ref(false)
const submittingPhone = ref(false)
const phoneFormRef = ref<FormInstance>()

const phoneForm = reactive({
  telephone: '',
  password: ''
})

const phoneRules = reactive<FormRules>({
  telephone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入登录密码', trigger: 'blur' }
  ]
})

const openPhoneDialog = () => {
  phoneForm.telephone = ''
  phoneForm.password = ''
  phoneDialogVisible.value = true
}

const submitPhone = async () => {
  if (!phoneFormRef.value) return
  await phoneFormRef.value.validate(async (valid) => {
    if (valid) {
      const isVerified = await verify()
      if (!isVerified) return

      submittingPhone.value = true
      try {
        const res = await userAPI.updatePhoneAPI({
          phone: phoneForm.telephone,
          password: phoneForm.password
        })
        if (res.code === 200) {
          ElMessage.success('手机号更新成功')
          phoneDialogVisible.value = false
          fetchSecurityData()
        } else {
          ElMessage.error(res.msg || '更新失败')
        }
      } catch (error) {
        ElMessage.error('网络请求失败')
      } finally {
        submittingPhone.value = false
      }
    }
  })
}

// ============== 实名认证 ==============
const realNameDialogVisible = ref(false)
const submittingRealName = ref(false)
const realNameFormRef = ref<FormInstance>()

const realNameForm = reactive({
  real_name: '',
  id_card: ''
})

const realNameRules = reactive<FormRules>({
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  id_card: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { validator: validateIdCard, trigger: 'blur' }
  ]
})

const openRealNameDialog = () => {
  realNameForm.real_name = ''
  realNameForm.id_card = ''
  realNameDialogVisible.value = true
}

const submitRealName = async () => {
  if (!realNameFormRef.value) return
  await realNameFormRef.value.validate(async (valid) => {
    if (valid) {
      submittingRealName.value = true
      try {
        const res = await userAPI.verifyRealNameAPI({
          real_name: realNameForm.real_name,
          id_card: realNameForm.id_card
        })
        if (res.code === 200) {
          ElMessage.success('实名认证资料已提交，等待平台审核')
          realNameDialogVisible.value = false
          fetchSecurityData()
        } else {
          ElMessage.error(res.msg || '认证失败')
        }
      } catch (error) {
        ElMessage.error('网络请求失败')
      } finally {
        submittingRealName.value = false
      }
    }
  })
}

onMounted(() => {
  fetchSecurityData()
})
</script>

<style scoped>
.security-container {
  flex: 1;
  padding: 28px;
  display: flex;
  flex-direction: column;
}

.security-header {
  margin-bottom: 24px;
}

.security-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #303133;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.security-card {
  flex: 1;
  border-radius: 12px;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.item-title .icon {
  font-size: 18px;
  color: #409eff;
}

.item-desc {
  font-size: 14px;
  color: #909399;
  padding-left: 26px;
}

.realname-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.static-status-tag {
  transition: none !important;
  animation: none !important;
  transform: none !important;
}
</style>
