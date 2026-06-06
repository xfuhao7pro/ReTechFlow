<template>
  <section class="admin-orders-page">
    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        class="keyword-input"
        placeholder="搜索订单号、商品、买家或卖家"
        clearable
        @keyup.enter="loadList"
      />
      <el-select v-model="query.status" class="status-select" placeholder="订单状态" @change="handleFilterChange">
        <el-option label="全部订单" value="all" />
        <el-option label="待付款" :value="0" />
        <el-option label="待发货" :value="1" />
        <el-option label="待收货" :value="2" />
        <el-option label="交易成功" :value="3" />
        <el-option label="交易取消" :value="4" />
        <el-option label="售后/退款中" :value="5" />
      </el-select>
      <el-button type="primary" @click="handleFilterChange">查询</el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="list"
      class="data-table"
      empty-text="暂无订单"
      row-key="order_id"
    >
      <el-table-column label="订单商品" min-width="300">
        <template #default="{ row }">
          <div class="goods-cell">
            <el-image class="goods-thumb" :src="getImageUrl(row.goods_image)" fit="cover">
              <template #error>
                <div class="image-fallback">无图</div>
              </template>
            </el-image>
            <div class="goods-meta">
              <strong>{{ row.goods_title || '商品信息已失效' }}</strong>
              <span class="order-id">订单号：{{ row.order_id }}</span>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="买家" min-width="150">
        <template #default="{ row }">
          <div class="user-cell">
            <el-avatar :size="28" :src="getImageUrl(row.buyer_avatar)">
              {{ getInitial(row.buyer_name) }}
            </el-avatar>
            <span>{{ row.buyer_name || '未知买家' }}</span>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="卖家" min-width="150">
        <template #default="{ row }">
          <div class="user-cell">
            <el-avatar :size="28" :src="getImageUrl(row.seller_avatar)">
              {{ getInitial(row.seller_name) }}
            </el-avatar>
            <span>{{ row.seller_name || '未知卖家' }}</span>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="金额" width="120">
        <template #default="{ row }">
          <span class="amount">￥{{ formatPrice(row.amount) }}</span>
        </template>
      </el-table-column>

      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="orderTagType(row.status)" effect="light">
            {{ orderStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="创建时间" width="170">
        <template #default="{ row }">
          {{ formatTime(row.created_at) || '-' }}
        </template>
      </el-table-column>

      <el-table-column label="操作" width="210" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openDetail(row)">详情</el-button>
          <el-button
            size="small"
            type="danger"
            plain
            :disabled="!row.goods_id"
            @click="offShelfGoods(row)"
          >
            下架商品
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager-wrap">
      <el-pagination
        layout="prev, pager, next, total"
        :total="total"
        :current-page="query.page"
        :page-size="query.page_size"
        @current-change="changePage"
      />
    </div>

    <el-dialog
      v-model="detailVisible"
      title="订单详情"
      width="680px"
      class="order-detail-dialog"
    >
      <div v-if="currentOrder" class="detail-panel">
        <div class="detail-goods">
          <el-image class="detail-thumb" :src="getImageUrl(currentOrder.goods_image)" fit="cover">
            <template #error>
              <div class="image-fallback">无图</div>
            </template>
          </el-image>
          <div>
            <strong>{{ currentOrder.goods_title || '商品信息已失效' }}</strong>
            <span>￥{{ formatPrice(currentOrder.amount) }}</span>
          </div>
        </div>

        <div class="detail-grid">
          <div class="detail-item">
            <span>订单号</span>
            <strong>{{ currentOrder.order_id }}</strong>
          </div>
          <div class="detail-item">
            <span>订单状态</span>
            <strong>{{ orderStatusText(currentOrder.status) }}</strong>
          </div>
          <div class="detail-item">
            <span>买家</span>
            <strong>{{ currentOrder.buyer_name || '未知买家' }}</strong>
          </div>
          <div class="detail-item">
            <span>卖家</span>
            <strong>{{ currentOrder.seller_name || '未知卖家' }}</strong>
          </div>
          <div class="detail-item">
            <span>创建时间</span>
            <strong>{{ formatTime(currentOrder.created_at) || '-' }}</strong>
          </div>
          <div class="detail-item">
            <span>付款时间</span>
            <strong>{{ formatTime(currentOrder.pay_time) || '-' }}</strong>
          </div>
          <div class="detail-item">
            <span>发货时间</span>
            <strong>{{ formatTime(currentOrder.consign_time) || '-' }}</strong>
          </div>
          <div class="detail-item">
            <span>物流单号</span>
            <strong>{{ currentOrder.tracking_number || '-' }}</strong>
          </div>
          <div class="detail-item full">
            <span>收货信息</span>
            <strong>
              {{ currentOrder.receiver_name || '-' }}
              {{ currentOrder.receiver_phone || '' }}
              {{ currentOrder.receiver_address || '' }}
            </strong>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button
          v-if="currentOrder?.goods_id"
          type="danger"
          plain
          @click="offShelfGoods(currentOrder)"
        >
          下架该商品
        </el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import adminApi from '@/api/adminapi'
import { formatPrice, formatTime, getImageUrl } from '@/utils/format'

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const detailVisible = ref(false)
const currentOrder = ref<any>(null)
const query = reactive({ page: 1, page_size: 10, status: 'all' as number | string, keyword: '' })

const orderStatusText = (status: number) => ({
  0: '待付款',
  1: '待发货',
  2: '待收货',
  3: '交易成功',
  4: '交易取消',
  5: '售后/退款中',
} as Record<number, string>)[status] || '未知'

const orderTagType = (status: number) => ({
  0: 'warning',
  1: 'warning',
  2: 'primary',
  3: 'success',
  4: 'info',
  5: 'danger',
} as Record<number, 'success' | 'warning' | 'info' | 'primary' | 'danger'>)[status] || 'info'

const getInitial = (name?: string) => (name || '?').trim().slice(0, 1).toUpperCase()

const loadList = async () => {
  loading.value = true
  try {
    const res = await adminApi.getOrders(query)
    list.value = res.data.list || []
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  query.page = 1
  loadList()
}

const changePage = (page: number) => {
  query.page = page
  loadList()
}

const openDetail = (row: any) => {
  currentOrder.value = row
  detailVisible.value = true
}

const offShelfGoods = async (row: any) => {
  if (!row?.goods_id) {
    ElMessage.warning('该订单关联商品已失效，无法下架')
    return
  }
  await ElMessageBox.confirm(
    `确定要下架「${row.goods_title || '该商品'}」吗？下架后交易广场将不再展示该商品。`,
    '下架商品',
    {
      confirmButtonText: '确认下架',
      cancelButtonText: '取消',
      type: 'warning',
    },
  )
  await adminApi.updateGoodsStatus(row.goods_id, 3, '后台订单监管下架')
  ElMessage.success('商品已下架')
  detailVisible.value = false
  loadList()
}

onMounted(loadList)
</script>

<style scoped>
.admin-orders-page {
  padding: 16px;
  border: 1px solid #e3eaf3;
  border-radius: 8px;
  background: #fff;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.keyword-input {
  max-width: 340px;
}

.status-select {
  width: 150px;
}

.data-table {
  margin-bottom: 14px;
}

.goods-cell {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: 12px;
}

.goods-thumb,
.detail-thumb {
  flex: 0 0 auto;
  width: 54px;
  height: 54px;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  background: #f8fafc;
}

.goods-meta {
  min-width: 0;
}

.goods-meta strong {
  display: block;
  overflow: hidden;
  color: #172033;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-id {
  display: block;
  margin-top: 5px;
  color: #64748b;
  font-size: 12px;
}

.user-cell {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: 8px;
}

.user-cell span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.amount {
  color: #dc2626;
  font-weight: 700;
}

.pager-wrap {
  display: flex;
  justify-content: flex-end;
}

.image-fallback {
  display: grid;
  width: 100%;
  height: 100%;
  place-items: center;
  color: #94a3b8;
  font-size: 12px;
}

.order-detail-dialog :deep(.el-dialog__body) {
  padding-top: 8px;
}

.detail-panel {
  display: grid;
  gap: 16px;
}

.detail-goods {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e8eef6;
  border-radius: 8px;
  background: #f8fafc;
}

.detail-goods strong,
.detail-goods span {
  display: block;
}

.detail-goods strong {
  color: #172033;
}

.detail-goods span {
  margin-top: 6px;
  color: #dc2626;
  font-weight: 700;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.detail-item {
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid #e8eef6;
  border-radius: 8px;
}

.detail-item.full {
  grid-column: 1 / -1;
}

.detail-item span,
.detail-item strong {
  display: block;
}

.detail-item span {
  margin-bottom: 6px;
  color: #64748b;
  font-size: 12px;
}

.detail-item strong {
  overflow-wrap: anywhere;
  color: #172033;
  font-size: 14px;
}

@media (max-width: 760px) {
  .toolbar {
    flex-wrap: wrap;
  }

  .keyword-input,
  .status-select {
    max-width: none;
    width: 100%;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
