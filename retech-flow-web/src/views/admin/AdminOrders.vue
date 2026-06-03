<template>
  <section class="admin-table-page">
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="搜索订单号/商品/买家/卖家" clearable @keyup.enter="loadList" />
      <el-select v-model="query.status" placeholder="状态" @change="loadList">
        <el-option label="全部" value="all" />
        <el-option label="待付款" :value="0" />
        <el-option label="待发货" :value="1" />
        <el-option label="待收货" :value="2" />
        <el-option label="交易成功" :value="3" />
        <el-option label="交易取消" :value="4" />
        <el-option label="售后/退款中" :value="5" />
      </el-select>
      <el-button type="primary" @click="loadList">查询</el-button>
    </div>

    <el-table v-loading="loading" :data="list" class="data-table" empty-text="暂无数据">
      <el-table-column prop="order_id" label="订单号" min-width="180" />
      <el-table-column label="商品" min-width="220">
        <template #default="{ row }">
          <div class="goods-title">{{ row.goods_title || '商品信息已失效' }}</div>
        </template>
      </el-table-column>
      <el-table-column prop="buyer_name" label="买家" width="120" />
      <el-table-column prop="seller_name" label="卖家" width="120" />
      <el-table-column prop="amount" label="金额" width="100" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="orderTagType(row.status)">{{ orderStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="收货信息" min-width="260">
        <template #default="{ row }">
          <span>{{ row.receiver_name }} {{ row.receiver_phone }} {{ row.receiver_address }}</span>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination layout="prev, pager, next, total" :total="total" :page-size="query.page_size" @current-change="changePage" />
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import adminApi from '@/api/adminapi'

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10, status: 'all' as any, keyword: '' })

const orderStatusText = (status: number) => ({ 0: '待付款', 1: '待发货', 2: '待收货', 3: '交易成功', 4: '交易取消', 5: '售后/退款中' } as Record<number, string>)[status] || '未知'
const orderTagType = (status: number) => ({ 0: 'warning', 1: 'warning', 2: 'primary', 3: 'success', 4: 'info', 5: 'danger' } as Record<number, any>)[status] || ''

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

const changePage = (page: number) => {
  query.page = page
  loadList()
}

onMounted(loadList)
</script>

<style scoped>
.admin-table-page {
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

.toolbar .el-input {
  max-width: 320px;
}

.goods-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.data-table {
  margin-bottom: 14px;
}
</style>
