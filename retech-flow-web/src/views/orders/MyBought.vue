<template>
  <DecorativeBackground>
    <div class="my-bought">
      <header class="mb-header">
        <div class="mb-header-text">
          <h1 class="mb-title">我买到的</h1>
          <p class="mb-sub">管理您的购买记录，追踪订单状态</p>
        </div>
        <div class="mb-header-actions">
          <el-button round @click="loadList">
            <el-icon class="el-icon--left"><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </header>

      <div class="mb-toolbar">
        <el-tabs v-model="filterStatus" class="status-tabs" @tab-change="applyFilter">
          <el-tab-pane label="全部" name="all" />
          <el-tab-pane label="待付款" :name="0" />
          <el-tab-pane label="待发货" :name="1" />
          <el-tab-pane label="待收货" :name="2" />
          <el-tab-pane label="交易成功" :name="3" />
          <el-tab-pane label="交易取消" :name="4" />
          <el-tab-pane label="售后/退款中" :name="5" />
        </el-tabs>
        <span class="mb-count">共 {{ orderList.length }} 笔订单</span>
      </div>

      <el-skeleton v-if="loading" :rows="6" animated class="mb-skeleton" />

      <template v-else-if="orderList.length > 0">
        <div class="order-list">
          <div class="order-item" v-for="order in orderList" :key="order.order_id">
            <div class="order-header">
              <span class="order-time">{{ formatDate(order.created_at) }}</span>
              <span class="order-no">订单号：{{ order.order_id }}</span>
              <span class="seller-name">卖家：{{ order.seller_name || order.seller?.nickname || '未知' }}</span>
              <div class="order-status" :class="getStatusClass(order.status)">
                {{ getStatusText(order.status) }}
              </div>
            </div>
            <div class="order-body">
              <div class="goods-info" @click="goToGoods(order.goods_id)">
                <el-image 
                  class="goods-img" 
                  :src="getImageUrl(order.goods_image)" 
                  fit="cover" 
                />
                <div class="goods-detail">
                  <div class="goods-title">{{ order.goods_title || '商品信息已失效' }}</div>
                  <div class="goods-price">¥ {{ formatPrice(order.amount) }}</div>
                </div>
              </div>
              <div class="order-actions">
                <el-button 
                  v-if="order.status === 0 || order.status === 1" 
                  type="danger" 
                  plain
                  size="small" 
                  @click="handleCancelOrder(order)"
                >
                  取消订单
                </el-button>
                <el-button 
                  v-if="order.status === 0" 
                  type="primary" 
                  size="small" 
                  @click="handlePay(order)"
                >
                  立即付款
                </el-button>
                <el-button 
                  v-if="order.status === 2 || order.status === 3" 
                  type="info" 
                  size="small"
                  @click="openLogisticsDialog(order)"
                >
                  查看物流
                </el-button>
                <el-button 
                  v-if="order.status === 2" 
                  type="success" 
                  size="small"
                  @click="handleConfirmReceipt(order)"
                >
                  确认收货
                </el-button>
              </div>
            </div>
            <div class="order-footer" v-if="order.receiver_name">
              <div class="delivery-info">
                <span class="label">收货信息：</span>
                <span>{{ order.receiver_name }} ({{ order.receiver_phone }}) {{ order.receiver_address }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <div v-else class="mb-empty-wrap">
        <el-empty description="暂无购买记录">
          <el-button type="primary" round @click="router.push('/market')">
            去逛逛
          </el-button>
        </el-empty>
      </div>

      <!-- 物流信息弹窗 -->
      <el-dialog
        v-model="logisticsDialogVisible"
        title="物流详情"
        width="600px"
        class="logistics-dialog"
      >
        <div v-loading="logisticsLoading" class="logistics-container">
          <template v-if="logisticsData">
            <div class="logistics-header">
              <div class="company-name">{{ logisticsData.company || '未知快递' }}</div>
              <div class="tracking-no">单号：{{ currentOrder?.tracking_number }}</div>
            </div>
            
            <div class="timeline-wrap" v-if="logisticsData.data && logisticsData.data.length > 0">
              <el-timeline>
                <el-timeline-item
                  v-for="(activity, index) in logisticsData.data"
                  :key="index"
                  :timestamp="activity.time"
                  :type="index === 0 ? 'primary' : 'info'"
                  :color="index === 0 ? '#409EFF' : ''"
                  :size="index === 0 ? 'large' : 'normal'"
                >
                  <span :class="{'latest-context': index === 0}">{{ activity.context }}</span>
                </el-timeline-item>
              </el-timeline>
            </div>
            <el-empty v-else description="暂无物流轨迹信息，请稍后再试" :image-size="100" />
          </template>
          <el-empty v-else-if="!logisticsLoading" description="获取物流信息失败" :image-size="100" />
        </div>
      </el-dialog>
    </div>
  </DecorativeBackground>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ordersApi from '@/api/ordersapi'
import DecorativeBackground from '@/components/DecorativeBackground.vue'
import { getImageUrl, formatPrice } from '@/utils/format'

const router = useRouter()
const loading = ref(false)
const orderList = ref<any[]>([])
const filterStatus = ref<'all' | number>('all')

// 物流弹窗相关状态
const logisticsDialogVisible = ref(false)
const logisticsLoading = ref(false)
const logisticsData = ref<any>(null)
const currentOrder = ref<any>(null)

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleString()
}

const getStatusText = (status: number) => {
  const map: Record<number, string> = {
    0: '待付款',
    1: '待发货',
    2: '待收货',
    3: '交易成功',
    4: '交易取消',
    5: '售后/退款中'
  }
  return map[status] || '未知状态'
}

const getStatusClass = (status: number) => {
  return {
    'status-pending': status === 0,
    'status-shipping': status === 1 || status === 2,
    'status-success': status === 3,
    'status-closed': status === 4 || status === 5
  }
}

function applyFilter() {
  loadList()
}

const loadList = async () => {
  loading.value = true
  try {
    const params: { status?: number | string } = {}
    if (filterStatus.value !== 'all') {
      params.status = filterStatus.value
    }
    
    const res = await ordersApi.getMyBoughtOrders(params)
    
    let dataList = []
    if (res && typeof res === 'object') {
      if (Array.isArray(res.data)) {
        dataList = res.data
      } else if (res.data && Array.isArray(res.data.list)) {
        dataList = res.data.list
      } else if (res.data && Array.isArray(res.data.results)) {
        dataList = res.data.results
      } else if (Array.isArray(res)) {
        dataList = res
      }
    }
    orderList.value = dataList
  } catch (e) {
    console.error('Failed to fetch orders:', e)
    orderList.value = []
  } finally {
    loading.value = false
  }
}

const goToGoods = (id: number | string) => {
  // 因为是从嵌套取出来，订单列表里不一定有 goods.id，实际可能需要把 goods_id 放进 serializer 里
  // 这里做一个保护
  if (id) {
    router.push(`/goods/${id}`)
  } else {
    ElMessage.warning('该商品可能已下架或删除')
  }
}

const handlePay = async (order: any) => {
  try {
    await ElMessageBox.confirm(`确认支付订单 ¥${formatPrice(order.amount)} 吗？`, '支付确认', {
      confirmButtonText: '确认支付',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    loading.value = true
    const res = await ordersApi.payOrder(order.order_id)
    if (res.code === 200) {
      ElMessage.success('支付成功')
      loadList()
    } else {
      ElMessage.error(res.msg || '支付失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error('支付请求出错')
    }
  } finally {
    loading.value = false
  }
}

// 打开查看物流弹窗
const openLogisticsDialog = async (order: any) => {
  currentOrder.value = order
  logisticsDialogVisible.value = true
  logisticsLoading.value = true
  logisticsData.value = null
  
  try {
    const res: any = await ordersApi.getOrderLogistics(order.order_id)
    if (res.code === 200) {
      logisticsData.value = {
        company: res.company,
        data: res.data
      }
    } else {
      ElMessage.error(res.msg || '获取物流信息失败')
    }
  } catch (error) {
    console.error('Logistics error:', error)
    ElMessage.error('网络请求失败')
  } finally {
    logisticsLoading.value = false
  }
}

// 取消订单
const handleCancelOrder = async (order: any) => {
  try {
    const tips = order.status === 1 
      ? '订单已付款，取消后金额将退回您的钱包。确定要取消吗？' 
      : '确定要取消该订单吗？取消后商品将重新上架。'
      
    await ElMessageBox.confirm(tips, '取消订单', {
      confirmButtonText: '确定取消',
      cancelButtonText: '暂不取消',
      type: 'warning'
    })
    
    loading.value = true
    const res = await ordersApi.cancelOrder(order.order_id)
    if (res.code === 200) {
      ElMessage.success('订单已取消')
      loadList()
    } else {
      ElMessage.error(res.msg || '取消失败')
    }
  } catch (e: any) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error('请求出错')
    }
  } finally {
    loading.value = false
  }
}

// 确认收货
const handleConfirmReceipt = async (order: any) => {
  try {
    await ElMessageBox.confirm('收到货了吗？确认后款项将直接打给卖家，且不可撤销哦！', '确认收货', {
      confirmButtonText: '确定收货',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    loading.value = true
    const res = await ordersApi.confirmReceipt(order.order_id)
    if (res.code === 200) {
      ElMessage.success('确认收货成功！')
      loadList()
    } else {
      ElMessage.error(res.msg || '确认收货失败')
    }
  } catch (e: any) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error('请求出错')
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadList()
})
</script>

<style scoped>
.my-bought {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.mb-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 32px;
  padding: 0;
  background: transparent;
  position: relative;
  z-index: 1;
}

.mb-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 6px;
  color: #303133;
  letter-spacing: -0.01em;
}

.mb-sub {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.mb-header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.mb-header-actions :deep(.el-button) {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(66, 165, 245, 0.2);
  color: #42a5f5;
  font-weight: 500;
  transition: all 0.3s ease;
}

.mb-header-actions :deep(.el-button:hover) {
  background: rgba(66, 165, 245, 0.1);
  border-color: #42a5f5;
  color: #1976d2;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 165, 245, 0.15);
}

.mb-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 28px;
  padding: 0;
  background: transparent;
  position: relative;
  z-index: 1;
}

.status-tabs {
  --el-tabs-header-height: 40px;
  flex: 1;
  margin-right: 20px;
}

.status-tabs :deep(.el-tabs__header) {
  margin: 0;
  border-bottom: none;
}

.status-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none; /* 去掉底部的长横线 */
}

.status-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  color: #606266;
  font-weight: 400;
  padding: 0 20px;
  transition: all 0.3s ease;
}

.status-tabs :deep(.el-tabs__item:hover) {
  color: #409eff;
}

.status-tabs :deep(.el-tabs__item.is-active) {
  color: #409eff;
  font-weight: 600;
}

.status-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 2px;
  background-color: #409eff;
  bottom: 0px;
}

.mb-count {
  font-size: 13px;
  font-weight: 600;
  color: #909399;
}

.mb-skeleton {
  padding: 12px 0;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.order-item {
  background: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.02);
}

.order-item:hover {
  box-shadow: 0 4px 16px 0 rgba(0,0,0,0.08);
  transform: translateY(-2px);
}

.order-header {
  background: #f5f7fa;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #606266;
}

.order-time {
  margin-right: 20px;
}

.order-no {
  margin-right: 20px;
}

.seller-name {
  flex: 1;
}

.order-status {
  font-weight: 600;
}
.order-status.status-pending { color: #f56c6c; }
.order-status.status-shipping { color: #e6a23c; }
.order-status.status-success { color: #67c23a; }
.order-status.status-closed { color: #909399; }

.order-body {
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.goods-info {
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  flex: 1;
}

.goods-img {
  width: 80px;
  height: 80px;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.goods-detail {
  flex: 1;
}

.goods-title {
  font-size: 15px;
  color: #303133;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-weight: 500;
  transition: color 0.2s;
}

.goods-info:hover .goods-title {
  color: #409eff;
}

.goods-price {
  font-size: 18px;
  font-weight: 600;
  color: #f56c6c;
}

.order-actions {
  min-width: 120px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-end;
}

.order-footer {
  padding: 12px 20px;
  background: #fafafa;
  border-top: 1px solid #f0f0f0;
  font-size: 13px;
  color: #606266;
}

.delivery-info .label {
  color: #909399;
}

.mb-empty-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 24px 48px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  border-radius: 16px;
  border: 2px dashed rgba(66, 165, 245, 0.25);
  position: relative;
  z-index: 1;
}

.mb-empty-wrap :deep(.el-empty__description) {
  color: #909399;
  font-weight: 500;
}

/* 物流详情弹窗样式 */
.logistics-dialog :deep(.el-dialog__body) {
  padding: 20px 24px;
  background: #fcfcfc;
}

.logistics-container {
  min-height: 200px;
}

.logistics-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.company-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.tracking-no {
  font-size: 14px;
  color: #606266;
}

.timeline-wrap {
  background: #ffffff;
  padding: 24px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  max-height: 400px;
  overflow-y: auto;
}

.timeline-wrap::-webkit-scrollbar {
  width: 6px;
}
.timeline-wrap::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}

.latest-context {
  color: #303133;
  font-weight: 500;
}
</style>