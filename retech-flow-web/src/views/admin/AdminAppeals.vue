<template>
  <section class="admin-appeals-page">
    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        class="keyword-input"
        placeholder="搜索订单号、商品、用户或申诉类型"
        clearable
        @keyup.enter="handleFilterChange"
      />
      <el-select v-model="query.status" class="status-select" placeholder="申诉状态" @change="handleFilterChange">
        <el-option label="全部申诉" value="all" />
        <el-option label="待处理" :value="0" />
        <el-option label="处理中" :value="1" />
        <el-option label="已裁决" :value="2" />
        <el-option label="已关闭" :value="3" />
      </el-select>
      <el-button type="primary" @click="handleFilterChange">查询</el-button>
    </div>

    <el-table v-loading="loading" :data="list" class="data-table" empty-text="暂无申诉">
      <el-table-column label="订单商品" min-width="280">
        <template #default="{ row }">
          <div class="goods-cell">
            <el-image class="thumb" :src="getImageUrl(row.goods_image)" fit="cover" />
            <div class="goods-meta">
              <strong>{{ row.goods_title || '商品信息已失效' }}</strong>
              <span>订单号：{{ row.order_id }}</span>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="申诉人" width="150">
        <template #default="{ row }">
          {{ row.applicant_name || '未知用户' }}（{{ row.applicant_role }}）
        </template>
      </el-table-column>
      <el-table-column prop="issue_type" label="申诉类型" width="150" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)">{{ appealStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="裁决结果" width="130">
        <template #default="{ row }">{{ resultText(row.result) }}</template>
      </el-table-column>
      <el-table-column label="提交时间" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openDetail(row)">查看</el-button>
          <el-button v-if="row.status === 0 || row.status === 1" size="small" type="primary" @click="openResolve(row)">
            裁决
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

    <el-dialog v-model="detailVisible" title="申诉详情" width="720px" class="appeal-dialog">
      <div v-if="currentAppeal" class="detail-panel">
        <div class="goods-card">
          <el-image class="detail-thumb" :src="getImageUrl(currentAppeal.goods_image)" fit="cover" />
          <div>
            <strong>{{ currentAppeal.goods_title || '商品信息已失效' }}</strong>
            <span>订单号：{{ currentAppeal.order_id }} ｜ 金额：￥{{ formatPrice(currentAppeal.order_amount) }}</span>
          </div>
        </div>

        <div class="detail-grid">
          <div class="detail-item">
            <span>买家</span>
            <strong>{{ currentAppeal.buyer_name || '-' }}</strong>
          </div>
          <div class="detail-item">
            <span>卖家</span>
            <strong>{{ currentAppeal.seller_name || '-' }}</strong>
          </div>
          <div class="detail-item">
            <span>申诉人</span>
            <strong>{{ currentAppeal.applicant_name }}（{{ currentAppeal.applicant_role }}）</strong>
          </div>
          <div class="detail-item">
            <span>申诉类型</span>
            <strong>{{ currentAppeal.issue_type }}</strong>
          </div>
          <div class="detail-item full">
            <span>问题描述</span>
            <strong>{{ currentAppeal.description }}</strong>
          </div>
          <div class="detail-item full" v-if="currentAppeal.admin_remark">
            <span>处理备注</span>
            <strong>{{ currentAppeal.admin_remark }}</strong>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button
          v-if="currentAppeal && (currentAppeal.status === 0 || currentAppeal.status === 1)"
          type="primary"
          @click="openResolve(currentAppeal)"
        >
          去裁决
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resolveVisible" title="仲裁裁决" width="520px" class="resolve-dialog">
      <el-form :model="resolveForm" label-width="92px">
        <el-form-item label="处理结果">
          <el-radio-group v-model="resolveForm.result">
            <el-radio value="refund_buyer">退款给买家</el-radio>
            <el-radio value="release_seller">放款给卖家</el-radio>
            <el-radio value="close">关闭申诉</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="处理备注">
          <el-input
            v-model="resolveForm.admin_remark"
            type="textarea"
            :rows="4"
            maxlength="300"
            show-word-limit
            placeholder="写明裁决依据，用户可看到该备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitResolve">确认裁决</el-button>
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
const submitting = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const detailVisible = ref(false)
const resolveVisible = ref(false)
const currentAppeal = ref<any>(null)
const query = reactive({ page: 1, page_size: 10, status: 0 as number | string, keyword: '' })
const resolveForm = reactive({
  result: 'refund_buyer' as 'refund_buyer' | 'release_seller' | 'close',
  admin_remark: '',
})

const appealStatusText = (status: number) => ({
  0: '待处理',
  1: '处理中',
  2: '已裁决',
  3: '已关闭',
} as Record<number, string>)[status] || '未知'

const statusTagType = (status: number) => ({
  0: 'warning',
  1: 'primary',
  2: 'success',
  3: 'info',
} as Record<number, 'success' | 'warning' | 'info' | 'primary'>)[status] || 'info'

const resultText = (result: string) => ({
  refund_buyer: '退款给买家',
  release_seller: '放款给卖家',
  close: '关闭申诉',
} as Record<string, string>)[result] || '未裁决'

const loadList = async () => {
  loading.value = true
  try {
    const res = await adminApi.getAppeals(query)
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
  currentAppeal.value = row
  detailVisible.value = true
}

const openResolve = (row: any) => {
  currentAppeal.value = row
  resolveForm.result = 'refund_buyer'
  resolveForm.admin_remark = ''
  resolveVisible.value = true
}

const submitResolve = async () => {
  if (!currentAppeal.value) return
  if (!resolveForm.admin_remark.trim()) {
    ElMessage.warning('请填写处理备注')
    return
  }
  const confirmText = resultText(resolveForm.result)
  await ElMessageBox.confirm(`确认执行「${confirmText}」吗？该操作会同步处理订单状态和余额。`, '确认裁决', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
  submitting.value = true
  try {
    await adminApi.resolveAppeal(currentAppeal.value.id, { ...resolveForm })
    ElMessage.success('申诉已处理')
    resolveVisible.value = false
    detailVisible.value = false
    loadList()
  } finally {
    submitting.value = false
  }
}

onMounted(loadList)
</script>

<style scoped>
.admin-appeals-page {
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

.goods-cell,
.goods-card {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: 12px;
}

.thumb,
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

.goods-meta strong,
.goods-meta span,
.goods-card strong,
.goods-card span {
  display: block;
}

.goods-meta strong {
  overflow: hidden;
  color: #172033;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.goods-meta span,
.goods-card span {
  margin-top: 5px;
  color: #64748b;
  font-size: 12px;
}

.pager-wrap {
  display: flex;
  justify-content: flex-end;
}

.detail-panel {
  display: grid;
  gap: 16px;
}

.goods-card {
  padding: 12px;
  border: 1px solid #e8eef6;
  border-radius: 8px;
  background: #f8fafc;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.detail-item {
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
  line-height: 1.7;
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
