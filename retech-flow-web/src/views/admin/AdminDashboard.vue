<template>
  <div class="dashboard" v-loading="loading">
    <div class="dashboard-hero">
      <div>
        <span class="eyebrow">运营看板</span>
        <h3>平台数据大屏</h3>
        <p>聚合用户、商品、订单、审核和公告数据，方便快速判断平台当前状态。</p>
      </div>
      <el-button type="primary" @click="loadDashboard">刷新数据</el-button>
    </div>

    <div class="metric-grid">
      <article v-for="item in statCards" :key="item.label" class="metric-card">
        <div class="metric-top">
          <span>{{ item.label }}</span>
          <i :class="item.tone"></i>
        </div>
        <strong>{{ item.value }}</strong>
        <em>{{ item.hint }}</em>
      </article>
    </div>

    <div class="main-grid">
      <section class="panel trend-panel">
        <div class="panel-title">
          <div>
            <h4>近 14 天增长趋势</h4>
            <span>新增用户、商品与订单变化</span>
          </div>
          <div class="legend">
            <span><i class="dot user"></i>用户</span>
            <span><i class="dot goods"></i>商品</span>
            <span><i class="dot order"></i>订单</span>
          </div>
        </div>

        <div class="line-chart">
          <svg viewBox="0 0 760 300" preserveAspectRatio="none" aria-label="近 14 天增长趋势图">
            <line v-for="y in gridLines" :key="y" x1="0" x2="760" :y1="y" :y2="y" class="grid-line" />
            <polyline :points="linePoints(userTrendValues)" class="line user-line" fill="none" />
            <polyline :points="linePoints(goodsTrendValues)" class="line goods-line" fill="none" />
            <polyline :points="linePoints(orderTrendValues)" class="line order-line" fill="none" />
          </svg>
          <div class="chart-dates">
            <span v-for="item in dateLabels" :key="item">{{ item }}</span>
          </div>
        </div>
      </section>

      <aside class="side-stack">
        <section class="panel todo-panel">
          <div class="panel-title compact">
            <div>
              <h4>待办事项</h4>
              <span>需要管理员处理</span>
            </div>
          </div>
          <div class="todo-list">
            <div v-for="item in todoCards" :key="item.label" class="todo-item">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
        </section>

        <section class="panel status-panel">
          <div class="panel-title compact">
            <div>
              <h4>订单状态</h4>
              <span>交易链路分布</span>
            </div>
          </div>
          <div class="status-list">
            <div v-for="item in orderStatusList" :key="item.label" class="status-row">
              <span>{{ item.label }}</span>
              <div class="track">
                <i :style="{ width: `${barPercent(item.value, orderStatusMax)}%` }"></i>
              </div>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
        </section>
      </aside>
    </div>

    <div class="secondary-grid">
      <section class="panel">
        <div class="panel-title">
          <div>
            <h4>交易金额趋势</h4>
            <span>已付款订单金额</span>
          </div>
          <strong class="panel-number">￥{{ formatAmount(totalPaidAmount) }}</strong>
        </div>
        <div class="bar-chart">
          <div v-for="item in amountTrend" :key="item.date" class="bar-item">
            <span class="bar" :style="{ height: `${barPercent(item.amount, amountMax)}%` }"></span>
            <small>{{ item.date }}</small>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <div>
            <h4>商品状态</h4>
            <span>审核与上下架分布</span>
          </div>
        </div>
        <div class="status-list roomy">
          <div v-for="item in goodsStatusList" :key="item.label" class="status-row">
            <span>{{ item.label }}</span>
            <div class="track goods-track">
              <i :style="{ width: `${barPercent(item.value, goodsStatusMax)}%` }"></i>
            </div>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <div>
            <h4>分类排行</h4>
            <span>标准机型库使用情况</span>
          </div>
        </div>
        <div class="rank-list">
          <div v-for="(item, index) in categoryRank" :key="item.name" class="rank-row">
            <b>{{ index + 1 }}</b>
            <span>{{ item.name }}</span>
            <div class="track">
              <i :style="{ width: `${barPercent(item.count, categoryMax)}%` }"></i>
            </div>
            <strong>{{ item.count }}</strong>
          </div>
          <el-empty v-if="categoryRank.length === 0" description="暂无分类数据" :image-size="72" />
        </div>
      </section>
    </div>

    <section class="panel records-panel">
      <div class="panel-title">
        <div>
          <h4>最新记录</h4>
          <span>最近商品、订单与公告</span>
        </div>
      </div>

      <div class="records-grid">
        <div>
          <h5>最新商品</h5>
          <el-table :data="dashboard?.recent_goods || []" height="260" empty-text="暂无商品">
            <el-table-column label="商品" min-width="220">
              <template #default="{ row }">
                <div class="goods-cell">
                  <el-image class="thumb" :src="getImageUrl(row.cover)" fit="cover" />
                  <span>{{ row.title || '未命名商品' }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="价格" width="90">
              <template #default="{ row }">￥{{ formatAmount(row.price) }}</template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">{{ goodsStatusText(row.status) }}</template>
            </el-table-column>
          </el-table>
        </div>

        <div>
          <h5>最新订单</h5>
          <el-table :data="dashboard?.recent_orders || []" height="260" empty-text="暂无订单">
            <el-table-column prop="order_id" label="订单号" min-width="160" />
            <el-table-column label="金额" width="90">
              <template #default="{ row }">￥{{ formatAmount(row.amount) }}</template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">{{ orderStatusText(row.status) }}</template>
            </el-table-column>
          </el-table>
        </div>

        <div>
          <h5>最新公告</h5>
          <div class="notice-list">
            <div v-for="item in dashboard?.recent_announcements || []" :key="item.id" class="notice-item">
              <strong>{{ item.title }}</strong>
              <span>{{ item.content }}</span>
            </div>
            <el-empty
              v-if="(dashboard?.recent_announcements || []).length === 0"
              description="暂无公告"
              :image-size="72"
            />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import adminApi from '@/api/adminapi'
import { getImageUrl } from '@/utils/format'

const loading = ref(false)
const dashboard = ref<any>(null)
const gridLines = [48, 108, 168, 228, 288]

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
    { label: '用户总数', value: cards.users || 0, hint: '平台注册账号', tone: 'blue' },
    { label: '商品总数', value: cards.goods || 0, hint: `${cards.pending_review_goods || 0} 个待审核`, tone: 'green' },
    { label: '在售商品', value: cards.on_sale_goods || 0, hint: '交易广场可见', tone: 'cyan' },
    { label: '订单总数', value: cards.orders || 0, hint: `${cards.pending_ship_orders || 0} 个待发货`, tone: 'orange' },
    { label: '成交金额', value: `￥${formatAmount(cards.paid_amount || 0)}`, hint: '已付款订单', tone: 'red' },
    { label: '生效公告', value: cards.active_announcements || 0, hint: '正在展示', tone: 'purple' },
  ]
})

const userTrendValues = computed(() => (dashboard.value?.charts?.user_trend || []).map((item: any) => item.count))
const goodsTrendValues = computed(() => (dashboard.value?.charts?.goods_trend || []).map((item: any) => item.count))
const orderTrendValues = computed(() => (dashboard.value?.charts?.order_trend || []).map((item: any) => item.count))
const dateLabels = computed(() => (dashboard.value?.charts?.order_trend || []).map((item: any) => item.date))
const amountTrend = computed(() => dashboard.value?.charts?.amount_trend || [])
const amountMax = computed(() => Math.max(1, ...amountTrend.value.map((item: any) => Number(item.amount || 0))))
const totalPaidAmount = computed(() => dashboard.value?.cards?.paid_amount || 0)

const categoryRank = computed<any[]>(() => dashboard.value?.charts?.category_rank || [])
const categoryMax = computed(() => Math.max(1, ...categoryRank.value.map((item: any) => Number(item.count || 0))))

const goodsStatusList = computed(() => {
  const status = dashboard.value?.goods_status || {}
  return Object.entries(goodsStatusMap).map(([key, label]) => ({ label, value: Number(status[key] || 0) }))
})
const goodsStatusMax = computed(() => Math.max(1, ...goodsStatusList.value.map(item => item.value)))

const orderStatusList = computed(() => {
  const status = dashboard.value?.order_status || {}
  return Object.entries(orderStatusMap).map(([key, label]) => ({ label, value: Number(status[key] || 0) }))
})
const orderStatusMax = computed(() => Math.max(1, ...orderStatusList.value.map(item => item.value)))

const todoCards = computed(() => {
  const todo = dashboard.value?.todo || {}
  return [
    { label: '商品待审核', value: todo.pending_goods || 0 },
    { label: '实名待审核', value: todo.pending_identity || 0 },
    { label: '订单待发货', value: todo.pending_ship_orders || 0 },
    { label: '售后订单', value: todo.after_sale_orders || 0 },
  ]
})

const barPercent = (value: number, max: number) => {
  if (!value) return 6
  return Math.max(6, Math.round((Number(value) / max) * 100))
}

const linePoints = (values: number[]) => {
  const width = 760
  const height = 240
  const top = 28
  const max = Math.max(1, ...userTrendValues.value, ...goodsTrendValues.value, ...orderTrendValues.value)
  if (!values.length) return ''
  return values.map((value, index) => {
    const x = values.length === 1 ? 0 : (index / (values.length - 1)) * width
    const y = top + height - (Number(value || 0) / max) * height
    return `${x},${y}`
  }).join(' ')
}

const formatAmount = (value: number | string) => {
  const num = Number(value || 0)
  if (Number.isNaN(num)) return '0'
  return num >= 10000 ? `${(num / 10000).toFixed(1)}万` : Number.isInteger(num) ? String(num) : num.toFixed(0)
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
  display: grid;
  gap: 18px;
  color: #172033;
}

.dashboard-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22px 24px;
  border: 1px solid #dbe6f2;
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(31, 94, 174, 0.1), rgba(255, 255, 255, 0) 42%),
    #ffffff;
}

.eyebrow {
  color: #1f5eae;
  font-size: 13px;
  font-weight: 800;
}

.dashboard-hero h3 {
  margin: 6px 0 6px;
  color: #0f172a;
  font-size: 26px;
  letter-spacing: 0;
}

.dashboard-hero p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12px;
}

.metric-card,
.panel {
  border: 1px solid #dfe8f2;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.04);
}

.metric-card {
  padding: 16px;
}

.metric-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.metric-top span,
.metric-card em {
  color: #64748b;
  font-size: 12px;
  font-style: normal;
}

.metric-top i {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.metric-top i.blue { background: #2563eb; }
.metric-top i.green { background: #16a34a; }
.metric-top i.cyan { background: #0891b2; }
.metric-top i.orange { background: #f97316; }
.metric-top i.red { background: #dc2626; }
.metric-top i.purple { background: #7c3aed; }

.metric-card strong {
  display: block;
  margin: 10px 0 7px;
  color: #0f172a;
  font-size: 26px;
  line-height: 1;
}

.main-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) 360px;
  gap: 16px;
}

.side-stack {
  display: grid;
  gap: 16px;
}

.panel {
  min-width: 0;
  padding: 18px;
}

.panel-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 16px;
}

.panel-title.compact {
  margin-bottom: 12px;
}

.panel-title h4,
.records-grid h5 {
  margin: 0;
  color: #0f172a;
  font-size: 16px;
}

.panel-title span {
  display: block;
  margin-top: 4px;
  color: #64748b;
  font-size: 12px;
}

.panel-number {
  color: #dc2626;
  font-size: 18px;
}

.legend {
  display: flex;
  gap: 14px;
  color: #475569;
  font-size: 12px;
  white-space: nowrap;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  margin-right: 6px;
  border-radius: 50%;
}

.dot.user { background: #2563eb; }
.dot.goods { background: #16a34a; }
.dot.order { background: #f97316; }

.line-chart {
  padding: 12px 12px 10px;
  border: 1px solid #edf2f7;
  border-radius: 8px;
  background: #f8fafc;
}

.line-chart svg {
  display: block;
  width: 100%;
  height: 300px;
}

.grid-line {
  stroke: #dbe5ef;
  stroke-width: 1;
}

.line {
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.user-line { stroke: #2563eb; }
.goods-line { stroke: #16a34a; }
.order-line { stroke: #f97316; }

.chart-dates {
  display: grid;
  grid-template-columns: repeat(14, minmax(0, 1fr));
  gap: 6px;
  margin-top: 8px;
  color: #94a3b8;
  font-size: 10px;
  text-align: center;
}

.todo-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.todo-item {
  padding: 14px;
  border: 1px solid #e8eef6;
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
  color: #0f172a;
  font-size: 26px;
  line-height: 1;
}

.status-list,
.rank-list {
  display: grid;
  gap: 11px;
}

.status-list.roomy {
  gap: 13px;
}

.status-row,
.rank-row {
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr) 34px;
  align-items: center;
  gap: 10px;
  color: #334155;
  font-size: 13px;
}

.rank-row {
  grid-template-columns: 24px 76px minmax(0, 1fr) 34px;
}

.rank-row b {
  display: grid;
  width: 22px;
  height: 22px;
  place-items: center;
  border-radius: 6px;
  background: #eef4ff;
  color: #1f5eae;
  font-size: 12px;
}

.track {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #edf2f7;
}

.track i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #1f5eae;
}

.goods-track i {
  background: #0891b2;
}

.secondary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.bar-chart {
  display: grid;
  grid-template-columns: repeat(14, minmax(0, 1fr));
  align-items: end;
  gap: 7px;
  height: 210px;
  padding: 8px 4px 0;
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
  max-width: 16px;
  border-radius: 999px 999px 2px 2px;
  background: linear-gradient(180deg, #1f5eae, #7aa9e8);
}

.bar-item small {
  color: #94a3b8;
  font-size: 10px;
  writing-mode: vertical-rl;
}

.records-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 0.8fr;
  gap: 16px;
}

.records-grid h5 {
  margin-bottom: 10px;
}

.goods-cell {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: 10px;
}

.goods-cell span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.thumb {
  flex: 0 0 auto;
  width: 42px;
  height: 42px;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  background: #f8fafc;
}

.notice-list {
  display: grid;
  gap: 10px;
}

.notice-item {
  padding: 12px;
  border: 1px solid #e8eef6;
  border-radius: 8px;
  background: #f8fafc;
}

.notice-item strong,
.notice-item span {
  display: block;
}

.notice-item strong {
  overflow: hidden;
  color: #172033;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notice-item span {
  display: -webkit-box;
  margin-top: 6px;
  overflow: hidden;
  color: #64748b;
  font-size: 12px;
  line-height: 1.6;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.dashboard :deep(.el-table) {
  --el-table-header-bg-color: #f8fafc;
  --el-table-tr-bg-color: #ffffff;
  --el-table-border-color: #edf2f7;
  font-size: 13px;
}

@media (max-width: 1320px) {
  .metric-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .main-grid,
  .secondary-grid,
  .records-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .dashboard-hero,
  .panel-title {
    flex-direction: column;
    align-items: stretch;
  }

  .metric-grid,
  .todo-list {
    grid-template-columns: 1fr;
  }

  .chart-dates span:nth-child(even) {
    display: none;
  }
}
</style>
