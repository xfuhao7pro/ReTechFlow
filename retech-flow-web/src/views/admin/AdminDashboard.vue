<template>
  <div class="dashboard" v-loading="loading">
    <div class="screen-header">
      <div>
        <span class="eyebrow">运营概览</span>
        <h3>平台数据大屏</h3>
      </div>
      <el-button type="primary" @click="loadDashboard">刷新数据</el-button>
    </div>

    <div class="metric-grid">
      <div class="metric-card" v-for="item in statCards" :key="item.label">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <em>{{ item.hint }}</em>
      </div>
    </div>

    <div class="content-grid">
      <section class="panel panel-wide">
        <div class="panel-title">
          <h4>近 14 天增长趋势</h4>
          <span>用户、商品、订单</span>
        </div>
        <div class="line-chart">
          <svg viewBox="0 0 720 260" preserveAspectRatio="none" aria-label="增长趋势图">
            <polyline :points="linePoints(userTrendValues)" class="line user-line" fill="none" />
            <polyline :points="linePoints(goodsTrendValues)" class="line goods-line" fill="none" />
            <polyline :points="linePoints(orderTrendValues)" class="line order-line" fill="none" />
          </svg>
          <div class="legend">
            <span><i class="dot user"></i>新增用户</span>
            <span><i class="dot goods"></i>新增商品</span>
            <span><i class="dot order"></i>新增订单</span>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h4>交易金额趋势</h4>
          <span>已付款订单金额</span>
        </div>
        <div class="bar-chart">
          <div class="bar-item" v-for="item in amountTrend" :key="item.date">
            <span class="bar" :style="{ height: `${barHeight(item.amount, amountMax)}%` }"></span>
            <small>{{ item.date }}</small>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h4>待办风险</h4>
          <span>需要人工处理</span>
        </div>
        <div class="todo-list">
          <div v-for="item in todoCards" :key="item.label" class="todo-item">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h4>商品状态分布</h4>
          <span>审核与交易状态</span>
        </div>
        <div class="rank-list">
          <div v-for="item in goodsStatusList" :key="item.label" class="rank-row">
            <span>{{ item.label }}</span>
            <div class="rank-track"><i :style="{ width: `${barHeight(item.value, goodsStatusMax)}%` }"></i></div>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h4>分类商品排行</h4>
          <span>标准机型库使用情况</span>
        </div>
        <div class="rank-list">
          <div v-for="item in categoryRank" :key="item.name" class="rank-row">
            <span>{{ item.name }}</span>
            <div class="rank-track"><i :style="{ width: `${barHeight(item.count, categoryMax)}%` }"></i></div>
            <strong>{{ item.count }}</strong>
          </div>
        </div>
      </section>

      <section class="panel panel-wide">
        <div class="panel-title">
          <h4>最新记录</h4>
          <span>商品、订单、公告</span>
        </div>
        <div class="recent-grid">
          <div>
            <h5>最新商品</h5>
            <el-table :data="dashboard?.recent_goods || []" height="260" empty-text="暂无数据">
              <el-table-column label="商品" min-width="220">
                <template #default="{ row }">
                  <div class="goods-cell">
                    <el-image class="thumb" :src="getImageUrl(row.cover)" fit="cover" />
                    <span>{{ row.title }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="price" label="价格" width="90" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">{{ goodsStatusText(row.status) }}</template>
              </el-table-column>
            </el-table>
          </div>
          <div>
            <h5>最新订单</h5>
            <el-table :data="dashboard?.recent_orders || []" height="260" empty-text="暂无数据">
              <el-table-column prop="order_id" label="订单号" min-width="160" />
              <el-table-column prop="amount" label="金额" width="90" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">{{ orderStatusText(row.status) }}</template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import adminApi from '@/api/adminapi'
import { getImageUrl } from '@/utils/format'

const loading = ref(false)
const dashboard = ref<any>(null)

const goodsStatusMap: Record<number, string> = {
  0: '草稿',
  1: '在售',
  2: '已售',
  3: '下架',
  4: '审核中',
  5: '审核驳回',
}

const orderStatusMap: Record<number, string> = {
  0: '待付款',
  1: '待发货',
  2: '待收货',
  3: '交易成功',
  4: '交易取消',
  5: '售后中',
}

const statCards = computed(() => {
  const cards = dashboard.value?.cards || {}
  return [
    { label: '用户总数', value: cards.users || 0, hint: '注册账号' },
    { label: '商品总数', value: cards.goods || 0, hint: `${cards.pending_review_goods || 0} 个待审核` },
    { label: '在售商品', value: cards.on_sale_goods || 0, hint: '交易广场可见' },
    { label: '订单总数', value: cards.orders || 0, hint: `${cards.pending_ship_orders || 0} 个待发货` },
    { label: '成交金额', value: `¥${Number(cards.paid_amount || 0).toFixed(0)}`, hint: '已付款订单' },
    { label: '公告数量', value: cards.active_announcements || 0, hint: '正在展示' },
  ]
})

const userTrendValues = computed(() => (dashboard.value?.charts?.user_trend || []).map((item: any) => item.count))
const goodsTrendValues = computed(() => (dashboard.value?.charts?.goods_trend || []).map((item: any) => item.count))
const orderTrendValues = computed(() => (dashboard.value?.charts?.order_trend || []).map((item: any) => item.count))
const amountTrend = computed(() => dashboard.value?.charts?.amount_trend || [])
const amountMax = computed(() => Math.max(1, ...amountTrend.value.map((item: any) => Number(item.amount || 0))))
const categoryRank = computed(() => dashboard.value?.charts?.category_rank || [])
const categoryMax = computed(() => Math.max(1, ...categoryRank.value.map((item: any) => Number(item.count || 0))))

const goodsStatusList = computed(() => {
  const status = dashboard.value?.goods_status || {}
  return Object.entries(goodsStatusMap).map(([key, label]) => ({
    label,
    value: Number(status[key] || 0),
  }))
})
const goodsStatusMax = computed(() => Math.max(1, ...goodsStatusList.value.map(item => item.value)))

const todoCards = computed(() => {
  const todo = dashboard.value?.todo || {}
  return [
    { label: '商品待审核', value: todo.pending_goods || 0 },
    { label: '实名待审核', value: todo.pending_identity || 0 },
    { label: '订单待发货', value: todo.pending_ship_orders || 0 },
    { label: '售后订单', value: todo.after_sale_orders || 0 },
  ]
})

const barHeight = (value: number, max: number) => {
  if (!value) return 8
  return Math.max(8, Math.round((Number(value) / max) * 100))
}

const linePoints = (values: number[]) => {
  const width = 720
  const height = 220
  const top = 20
  const max = Math.max(1, ...values)
  if (!values.length) return ''
  return values.map((value, index) => {
    const x = values.length === 1 ? 0 : (index / (values.length - 1)) * width
    const y = top + height - (Number(value || 0) / max) * height
    return `${x},${y}`
  }).join(' ')
}

const goodsStatusText = (status: number) => goodsStatusMap[status] || '未知'
const orderStatusText = (status: number) => orderStatusMap[status] || '未知'

const loadDashboard = async () => {
  loading.value = true
  try {
    const res = await adminApi.getDashboard()
    dashboard.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>

<style scoped>
.dashboard {
  color: #172033;
}

.screen-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.eyebrow {
  color: #1d5fb8;
  font-size: 13px;
  font-weight: 700;
}

.screen-header h3 {
  margin: 5px 0 0;
  font-size: 24px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.metric-card,
.panel {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
}

.metric-card {
  padding: 16px;
}

.metric-card span,
.metric-card em {
  display: block;
  color: #64748b;
  font-size: 12px;
  font-style: normal;
}

.metric-card strong {
  display: block;
  margin: 9px 0 6px;
  color: #0f172a;
  font-size: 26px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.panel {
  padding: 16px;
  min-height: 250px;
}

.panel-wide {
  grid-column: span 2;
}

.panel-title {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 14px;
}

.panel-title h4,
.recent-grid h5 {
  margin: 0;
  font-size: 16px;
}

.panel-title span {
  color: #64748b;
  font-size: 12px;
}

.line-chart svg {
  width: 100%;
  height: 260px;
  border-radius: 8px;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}

.line {
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.user-line {
  stroke: #2563eb;
}

.goods-line {
  stroke: #16a34a;
}

.order-line {
  stroke: #f97316;
}

.legend {
  display: flex;
  gap: 18px;
  margin-top: 10px;
  color: #475569;
  font-size: 13px;
}

.dot {
  display: inline-block;
  width: 9px;
  height: 9px;
  margin-right: 6px;
  border-radius: 50%;
}

.dot.user {
  background: #2563eb;
}

.dot.goods {
  background: #16a34a;
}

.dot.order {
  background: #f97316;
}

.bar-chart {
  display: grid;
  grid-template-columns: repeat(14, minmax(0, 1fr));
  align-items: end;
  gap: 8px;
  height: 220px;
  padding-top: 12px;
}

.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
  gap: 8px;
}

.bar {
  width: 100%;
  max-width: 18px;
  border-radius: 999px 999px 0 0;
  background: #1d5fb8;
}

.bar-item small {
  color: #94a3b8;
  font-size: 10px;
  writing-mode: vertical-rl;
}

.todo-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.todo-item {
  padding: 16px;
  border-radius: 8px;
  background: #f8fafc;
}

.todo-item span {
  color: #64748b;
  font-size: 13px;
}

.todo-item strong {
  display: block;
  margin-top: 8px;
  font-size: 28px;
}

.rank-list {
  display: grid;
  gap: 12px;
}

.rank-row {
  display: grid;
  grid-template-columns: 86px minmax(0, 1fr) 36px;
  align-items: center;
  gap: 10px;
  color: #334155;
  font-size: 13px;
}

.rank-track {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #e2e8f0;
}

.rank-track i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #1d5fb8;
}

.recent-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.recent-grid h5 {
  margin-bottom: 10px;
}

.goods-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.thumb {
  width: 42px;
  height: 42px;
  border-radius: 6px;
}

@media (max-width: 1180px) {
  .metric-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .content-grid,
  .recent-grid {
    grid-template-columns: 1fr;
  }

  .panel-wide {
    grid-column: span 1;
  }
}
</style>
