<template>
  <section class="review-page">
    <header class="page-head">
      <div>
        <h2>商品审核</h2>
        <p>核对商品图片、描述和机型属性后处理上架申请</p>
      </div>
      <div class="head-count"><strong>{{ total }}</strong><span>条记录</span></div>
    </header>

    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="搜索商品或卖家" clearable @keyup.enter="search">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="query.status" placeholder="商品状态" @change="search">
        <el-option label="全部状态" value="all" />
        <el-option label="草稿" :value="0" />
        <el-option label="在售" :value="1" />
        <el-option label="已售" :value="2" />
        <el-option label="已下架" :value="3" />
        <el-option label="待审核" :value="4" />
        <el-option label="审核驳回" :value="5" />
      </el-select>
      <el-button type="primary" @click="search">查询</el-button>
      <el-button :icon="Refresh" circle title="刷新" @click="loadList" />
    </div>

    <el-table v-loading="loading" :data="list" class="data-table" empty-text="暂无商品记录">
      <el-table-column label="商品" min-width="320">
        <template #default="{ row }">
          <div class="goods-cell">
            <el-image class="thumb" :src="getImageUrl(row.cover)" fit="cover" />
            <div class="goods-copy">
              <strong>{{ row.title || '未命名商品' }}</strong>
              <span>{{ row.seller?.nickname || '未命名用户' }} · {{ row.category?.name || '未分类' }}</span>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="价格" width="120">
        <template #default="{ row }"><b class="price">¥{{ formatPrice(row.price) }}</b></template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }"><el-tag :type="goodsTagType(row.status)">{{ goodsStatusText(row.status) }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="views" label="浏览" width="80" />
      <el-table-column label="提交时间" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" :icon="View" @click="openDetail(row)">查看详情</el-button>
          <el-button v-if="[4, 5].includes(row.status)" link type="success" @click="approveGoods(row)">通过</el-button>
          <el-button v-if="row.status === 4" link type="danger" @click="rejectGoods(row)">驳回</el-button>
          <el-button v-if="row.status === 1" link type="warning" @click="offShelf(row)">下架</el-button>
        </template>
      </el-table-column>
    </el-table>

    <footer class="table-footer">
      <span>共 {{ total }} 条</span>
      <el-pagination v-model:current-page="query.page" layout="prev, pager, next" :total="total" :page-size="query.page_size" @current-change="loadList" />
    </footer>

    <el-drawer v-model="detailVisible" title="商品审核详情" size="min(760px, 92vw)" destroy-on-close>
      <div v-if="currentGoods" class="detail-body">
        <section class="detail-hero">
          <div class="gallery">
            <el-image
              v-for="image in goodsImages"
              :key="image.id || image.image"
              :src="getImageUrl(image.image)"
              :preview-src-list="goodsImages.map((item: any) => getImageUrl(item.image))"
              fit="cover"
            />
            <el-empty v-if="goodsImages.length === 0" description="未上传图片" :image-size="70" />
          </div>
          <div class="summary">
            <el-tag :type="goodsTagType(currentGoods.status)">{{ goodsStatusText(currentGoods.status) }}</el-tag>
            <h3>{{ currentGoods.title || '未命名商品' }}</h3>
            <strong class="detail-price">¥{{ formatPrice(currentGoods.price) }}</strong>
            <div class="seller-line">
              <el-avatar :size="34" :src="getImageUrl(currentGoods.seller?.avatar)" />
              <div><b>{{ currentGoods.seller?.nickname || '未命名用户' }}</b><span>{{ currentGoods.seller?.email || '未提供邮箱' }}</span></div>
            </div>
          </div>
        </section>

        <section class="detail-section">
          <h4>商品信息</h4>
          <dl class="info-grid">
            <div><dt>商品分类</dt><dd>{{ currentGoods.category?.name || '未分类' }}</dd></div>
            <div><dt>交付方式</dt><dd>{{ currentGoods.delivery_method || '未填写' }}</dd></div>
            <div><dt>浏览次数</dt><dd>{{ currentGoods.views || 0 }}</dd></div>
            <div><dt>收藏人数</dt><dd>{{ currentGoods.wants || 0 }}</dd></div>
            <div><dt>提交时间</dt><dd>{{ formatTime(currentGoods.created_at) }}</dd></div>
            <div><dt>更新时间</dt><dd>{{ formatTime(currentGoods.updated_at) }}</dd></div>
          </dl>
        </section>

        <section v-if="attributeEntries.length" class="detail-section">
          <h4>机型属性</h4>
          <dl class="attribute-list">
            <div v-for="([key, value]) in attributeEntries" :key="key"><dt>{{ key }}</dt><dd>{{ value }}</dd></div>
          </dl>
        </section>

        <section class="detail-section">
          <h4>商品描述</h4>
          <p class="description">{{ currentGoods.description || '未填写商品描述' }}</p>
        </section>

        <section v-if="currentGoods.audit_reason" class="audit-reason">
          <b>上次驳回原因</b><p>{{ currentGoods.audit_reason }}</p>
        </section>
      </div>

      <template #footer>
        <div class="drawer-actions">
          <el-button @click="detailVisible = false">关闭</el-button>
          <el-button v-if="currentGoods?.status === 4" type="danger" plain @click="rejectGoods(currentGoods)">驳回申请</el-button>
          <el-button v-if="[4, 5].includes(currentGoods?.status)" type="primary" @click="approveGoods(currentGoods)">审核通过</el-button>
          <el-button v-if="currentGoods?.status === 1" type="warning" plain @click="offShelf(currentGoods)">下架商品</el-button>
        </div>
      </template>
    </el-drawer>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search, View } from '@element-plus/icons-vue'
import adminApi from '@/api/adminapi'
import { getImageUrl } from '@/utils/format'

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const detailVisible = ref(false)
const currentGoods = ref<any>(null)
const query = reactive({ page: 1, page_size: 10, status: 4 as any, keyword: '' })

const goodsStatusText = (status: number) => ({ 0: '草稿', 1: '在售', 2: '已售', 3: '已下架', 4: '待审核', 5: '审核驳回' } as Record<number, string>)[status] || '未知'
const goodsTagType = (status: number) => ({ 1: 'success', 2: 'info', 3: 'warning', 4: 'primary', 5: 'danger' } as Record<number, any>)[status] || 'info'
const formatPrice = (value: unknown) => Number(value || 0).toFixed(2)
const formatTime = (value?: string) => value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '-'
const goodsImages = computed(() => currentGoods.value?.images || [])
const attributeEntries = computed(() => Object.entries(currentGoods.value?.attributes || {}))

const loadList = async () => {
  loading.value = true
  try {
    const res = await adminApi.getGoods(query)
    list.value = res.data.list || []
    total.value = res.data.total || 0
    if (currentGoods.value) currentGoods.value = list.value.find(item => item.id === currentGoods.value.id) || currentGoods.value
  } finally {
    loading.value = false
  }
}

const search = () => { query.page = 1; loadList() }
const openDetail = (row: any) => { currentGoods.value = row; detailVisible.value = true }

const updateStatus = async (row: any, status: number, reason = '') => {
  await adminApi.updateGoodsStatus(row.id, status, reason)
  ElMessage.success(status === 1 ? '商品已通过审核' : status === 3 ? '商品已下架' : '商品已驳回')
  detailVisible.value = false
  await loadList()
}

const approveGoods = async (row: any) => {
  await ElMessageBox.confirm(`确认通过“${row.title || '该商品'}”的上架审核吗？`, '审核确认', { confirmButtonText: '确认通过', cancelButtonText: '取消', type: 'success' })
  await updateStatus(row, 1)
}

const rejectGoods = async (row: any) => {
  const { value } = await ElMessageBox.prompt('请填写具体驳回原因，卖家将据此修改商品。', '驳回商品', { confirmButtonText: '确认驳回', cancelButtonText: '取消', inputType: 'textarea', inputPattern: /\S+/, inputErrorMessage: '请填写驳回原因' })
  await updateStatus(row, 5, value)
}

const offShelf = async (row: any) => {
  await ElMessageBox.confirm(`下架后“${row.title || '该商品'}”将不再出现在交易广场。`, '确认下架', { confirmButtonText: '确认下架', cancelButtonText: '取消', type: 'warning' })
  await updateStatus(row, 3)
}

onMounted(loadList)
</script>

<style scoped>
.review-page { padding: 20px; border: 1px solid #dfe7f0; border-radius: 8px; background: #fff; color: #172033; }
.page-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 20px; margin-bottom: 20px; }
.page-head h2 { margin: 0; font-size: 20px; }
.page-head p { margin: 6px 0 0; color: #718096; font-size: 13px; }
.head-count { display: flex; align-items: baseline; gap: 5px; color: #718096; font-size: 12px; }
.head-count strong { color: #1d4f91; font-size: 24px; font-variant-numeric: tabular-nums; }
.toolbar { display: grid; grid-template-columns: minmax(220px, 360px) 150px auto auto; gap: 10px; margin-bottom: 16px; padding: 14px; border-radius: 7px; background: #f6f8fb; }
.goods-cell, .seller-line { display: flex; align-items: center; gap: 12px; min-width: 0; }
.thumb { flex: 0 0 auto; width: 56px; height: 56px; border: 1px solid #e2e8f0; border-radius: 7px; background: #f8fafc; }
.goods-copy { min-width: 0; }
.goods-copy strong, .goods-copy span { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.goods-copy span, .seller-line span { margin-top: 5px; color: #718096; font-size: 12px; }
.price { color: #d94841; font-variant-numeric: tabular-nums; }
.data-table { margin-bottom: 12px; }
.table-footer { display: flex; align-items: center; justify-content: space-between; color: #718096; font-size: 13px; }
.detail-body { display: grid; gap: 24px; padding: 0 4px 20px; }
.detail-hero { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(220px, .75fr); gap: 22px; }
.gallery { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; min-height: 150px; }
.gallery .el-image { width: 100%; aspect-ratio: 1; border-radius: 7px; background: #f1f5f9; }
.summary { padding: 4px 0; }
.summary h3 { margin: 12px 0 8px; font-size: 20px; line-height: 1.5; }
.detail-price { display: block; margin-bottom: 22px; color: #d94841; font-size: 26px; }
.seller-line { padding-top: 16px; border-top: 1px solid #edf1f5; }
.seller-line b, .seller-line span { display: block; }
.detail-section h4 { margin: 0 0 12px; font-size: 15px; }
.info-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); margin: 0; border-top: 1px solid #e8edf3; border-left: 1px solid #e8edf3; }
.info-grid div { padding: 12px 14px; border-right: 1px solid #e8edf3; border-bottom: 1px solid #e8edf3; }
.info-grid dt, .attribute-list dt { color: #718096; font-size: 12px; }
.info-grid dd, .attribute-list dd { margin: 5px 0 0; color: #1f2937; }
.attribute-list { display: flex; flex-wrap: wrap; gap: 8px; margin: 0; }
.attribute-list div { min-width: 150px; padding: 10px 12px; border-radius: 6px; background: #f6f8fb; }
.description { margin: 0; padding: 14px; border-left: 3px solid #7fa5d1; background: #f7f9fc; color: #46556b; line-height: 1.8; white-space: pre-wrap; }
.audit-reason { padding: 14px; border: 1px solid #f2c7c4; border-radius: 7px; background: #fff7f6; color: #a33c37; }
.audit-reason p { margin: 6px 0 0; line-height: 1.7; }
.drawer-actions { display: flex; justify-content: flex-end; gap: 8px; }
@media (max-width: 760px) { .review-page { padding: 14px; } .page-head { flex-direction: column; } .toolbar { grid-template-columns: 1fr; } .detail-hero { grid-template-columns: 1fr; } .info-grid { grid-template-columns: 1fr; } }
</style>
