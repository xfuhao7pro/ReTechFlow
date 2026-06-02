<template>
  <DecorativeBackground>
  <div class="wallet-container">
    <div class="wallet-header">
      <h2>资产钱包</h2>
      <p class="subtitle">管理您的账户余额及交易记录</p>
    </div>

    <el-row :gutter="24">
      <el-col :span="8">
        <el-card class="balance-card" shadow="never" v-loading="loading">
          <div class="balance-title">
            <el-icon class="icon"><Wallet /></el-icon>
            <span>可用余额</span>
          </div>
          <div class="balance-amount">
            <span class="currency">¥</span>
            <span class="value">{{ walletData.balance }}</span>
          </div>
          <div class="balance-actions">
            <el-button type="primary" round class="action-btn" @click="showRechargeDialog = true">充值</el-button>
            <el-button round class="action-btn">提现</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card class="record-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>近期交易记录</span>
            </div>
          </template>
          <el-empty description="暂无交易记录" :image-size="100" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 充值弹窗 -->
    <el-dialog v-model="showRechargeDialog" title="账户充值" width="400px" destroy-on-close>
      <div class="recharge-content">
        <el-form label-position="top">
          <el-form-item label="充值金额 (元)">
            <el-input-number 
              v-model="rechargeAmount" 
              :min="0.01" 
              :precision="2" 
              :step="100" 
              style="width: 100%;"
              placeholder="请输入充值金额" 
            />
          </el-form-item>
          <div class="quick-amount">
            <el-button size="small" @click="rechargeAmount = 50">50元</el-button>
            <el-button size="small" @click="rechargeAmount = 100">100元</el-button>
            <el-button size="small" @click="rechargeAmount = 500">500元</el-button>
            <el-button size="small" @click="rechargeAmount = 1000">1000元</el-button>
          </div>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRechargeDialog = false">取消</el-button>
          <el-button type="primary" @click="handleRecharge" :loading="recharging">确认充值</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
  </DecorativeBackground>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Wallet } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import userAPI from '@/api/userapi'
import type { WalletData } from '@/api/userapi'
import DecorativeBackground from '@/components/DecorativeBackground.vue'

const loading = ref(true)
const showRechargeDialog = ref(false)
const recharging = ref(false)
const rechargeAmount = ref(100.00)

const walletData = reactive<WalletData>({
  balance: '0.00'
})

const fetchWalletData = async () => {
  loading.value = true
  try {
    const res = await userAPI.getWalletAPI()
    if (res.code === 200 && res.data) {
      walletData.balance = res.data.balance || '0.00'
    } else {
      ElMessage.error(res.msg || '获取钱包信息失败')
    }
  } catch (error) {
    console.error('获取钱包信息出错:', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

const handleRecharge = async () => {
  if (!rechargeAmount.value || rechargeAmount.value <= 0) {
    ElMessage.warning('请输入有效的充值金额')
    return
  }
  recharging.value = true
  try {
    const res = await userAPI.rechargeWalletAPI(rechargeAmount.value)
    if (res.code === 200) {
      ElMessage.success(res.msg || '充值成功')
      showRechargeDialog.value = false
      // 刷新余额
      await fetchWalletData()
    } else {
      ElMessage.error(res.msg || '充值失败')
    }
  } catch (error) {
    console.error('充值出错:', error)
    ElMessage.error('网络请求失败')
  } finally {
    recharging.value = false
  }
}

onMounted(() => {
  fetchWalletData()
})
</script>

<style scoped>
.wallet-container {
  flex: 1;
  padding: 28px;
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.wallet-header {
  margin-bottom: 24px;
}

.wallet-header h2 {
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

.balance-card {
  border-radius: 12px;
  background: linear-gradient(135deg, #f0f7ff 0%, #e6f3ff 100%);
  border: 1px solid #d9ecff;
  text-align: center;
  padding: 20px 0;
}

.balance-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #606266;
  font-size: 15px;
  margin-bottom: 16px;
}

.balance-title .icon {
  font-size: 20px;
  color: #409eff;
}

.balance-amount {
  color: #303133;
  margin-bottom: 30px;
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
}

.currency {
  font-size: 20px;
  font-weight: 600;
}

.value {
  font-size: 40px;
  font-weight: 700;
  font-family: 'DIN Alternate', 'Helvetica Neue', sans-serif;
  letter-spacing: -1px;
}

.balance-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.action-btn {
  width: 100px;
}

.record-card {
  border-radius: 12px;
  height: 100%;
}

.card-header {
  font-weight: 600;
  color: #303133;
}

.recharge-content {
  padding: 10px 0;
}

.quick-amount {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}
</style>
