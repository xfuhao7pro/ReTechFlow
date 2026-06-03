<template>
  <section class="admin-table-page">
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="搜索商品或卖家" clearable @keyup.enter="loadList" />
      <el-select v-model="query.status" placeholder="状态" @change="loadList">
        <el-option label="全部" value="all" />
        <el-option label="草稿" :value="0" />
        <el-option label="在售" :value="1" />
        <el-option label="已售" :value="2" />
        <el-option label="下架" :value="3" />
        <el-option label="审核中" :value="4" />
        <el-option label="审核驳回" :value="5" />
      </el-select>
      <el-button type="primary" @click="loadList">查询</el-button>
    </div>

    <el-table v-loading="loading" :data="list" class="data-table" empty-text="暂无数据">
      <el-table-column label="商品" min-width="280">
        <template #default="{ row }">
          <div class="goods-cell">
            <el-image class="thumb" :src="getImageUrl(row.cover)" fit="cover" />
            <div>
              <strong>{{ row.title || '未命名商品' }}</strong>
              <span>{{ row.seller?.nickname || '未知卖家' }}</span>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="price" label="价格" width="110" />
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="goodsTagType(row.status)">{{ goodsStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="views" label="浏览" width="90" />
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button v-if="row.status === 4 || row.status === 5" size="small" type="success" @click="setStatus(row.id, 1)">通过</el-button>
          <el-button v-if="row.status === 4" size="small" type="danger" plain @click="rejectGoods(row)">驳回</el-button>
          <el-button v-if="row.status === 1" size="small" @click="setStatus(row.id, 3)">下架</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination layout="prev, pager, next, total" :total="total" :page-size="query.page_size" @current-change="changePage" />
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import adminApi from '@/api/adminapi'
import { getImageUrl } from '@/utils/format'

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10, status: 4 as any, keyword: '' })

const goodsStatusText = (status: number) => ({ 0: '草稿', 1: '在售', 2: '已售', 3: '下架', 4: '审核中', 5: '审核驳回' } as Record<number, string>)[status] || '未知'
const goodsTagType = (status: number) => ({ 1: 'success', 2: 'info', 3: 'warning', 4: 'primary', 5: 'danger' } as Record<number, any>)[status] || ''

const loadList = async () => {
  loading.value = true
  try {
    const res = await adminApi.getGoods(query)
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

const setStatus = async (id: string, status: number) => {
  await adminApi.updateGoodsStatus(id, status)
  ElMessage.success('商品状态已更新')
  loadList()
}

const rejectGoods = async (row: any) => {
  const { value } = await ElMessageBox.prompt('请输入驳回原因，用户会在“我发布的”里看到该备注。', '驳回商品', {
    confirmButtonText: '确认驳回',
    cancelButtonText: '取消',
    inputPattern: /\S+/,
    inputErrorMessage: '请填写驳回原因',
  })
  await adminApi.updateGoodsStatus(row.id, 5, value)
  ElMessage.success('已驳回该商品')
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
  max-width: 280px;
}

.goods-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.goods-cell strong,
.goods-cell span {
  display: block;
}

.goods-cell span {
  margin-top: 5px;
  color: #64748b;
  font-size: 12px;
}

.thumb {
  width: 52px;
  height: 52px;
  border-radius: 6px;
}

.data-table {
  margin-bottom: 14px;
}
</style>
