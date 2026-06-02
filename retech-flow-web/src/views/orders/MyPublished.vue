<template>
  <DecorativeBackground>
    <div class="my-published">
      <header class="mp-header">
        <div class="mp-header-text">
          <h1 class="mp-title">我发布的</h1>
          <p class="mp-sub">管理你上架的宝贝，瀑布流浏览更直观</p>
        </div>
        <div class="mp-header-actions">
          <el-button class="btn-publish" type="primary" round @click="goPublish">
            <el-icon class="el-icon--left"><Plus /></el-icon>
            去发布
          </el-button>
          <el-button round @click="loadList">
            <el-icon class="el-icon--left"><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </header>

      <div class="mp-toolbar">
        <el-tabs v-model="filterStatus" class="status-tabs" @tab-change="applyFilter">
          <el-tab-pane label="全部" name="all" />
          <el-tab-pane label="在售" :name="1" />
          <el-tab-pane label="已售出" :name="3" />
          <el-tab-pane label="已下架" :name="2" />
        </el-tabs>
        
        <div class="mp-search">
          <SearchBox
            v-model="searchKeyword"
            placeholder="搜索我发布的商品"
            @search="handleSearch"
          />
        </div>
        <span class="mp-count">共 {{ rawList.length }} 件</span>
      </div>

      <el-skeleton v-if="loading" :rows="6" animated class="mp-skeleton" />

      <template v-else-if="rawList.length">
        <div class="waterfall" role="list">
          <GoodsCard
            v-for="item in rawList"
            :key="item.id"
            :item="item"
            :show-status="true"
            meta-type="views"
          />
        </div>
      </template>

      <div v-else class="mp-empty-wrap">
        <el-empty description="还没有发布过商品">
          <el-button class="btn-publish" type="primary" round @click="goPublish">
            <el-icon class="el-icon--left"><Plus /></el-icon>
            去发布
          </el-button>
        </el-empty>
      </div>
    </div>
  </DecorativeBackground>
</template>

<script lang="ts" setup name="MyPublished">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Refresh } from '@element-plus/icons-vue'
import goodsApi, { type MyPublishedItem } from '@/api/goodsapi'
import GoodsCard from '@/components/GoodsCard.vue'
import DecorativeBackground from '@/components/DecorativeBackground.vue'
import SearchBox from '@/components/SearchBox.vue'

const router = useRouter()

const loading = ref(true)
const rawList = ref<MyPublishedItem[]>([])
const filterStatus = ref<'all' | number>('all')
const searchKeyword = ref('')

function applyFilter() {
  loadList()
}

function handleSearch() {
  loadList()
}

function goPublish() {
  router.push({ name: 'Publish' })
}

async function loadList() {
  loading.value = true
  try {
    const params: { status?: number, keyword?: string } = {}
    if (filterStatus.value !== 'all') {
      params.status = filterStatus.value as number
    }
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    
    const res = await goodsApi.listMyPublishedAPI(params)

    // 需要判断真实的列表数据在哪里
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
    
    console.log('解析后的列表数据:', dataList)

    if (dataList.length > 0) {
      rawList.value = dataList.map((item: any) => ({
        ...item,
        statusText: undefined, // GoodsCard will handle it
      }))
    } else {
      rawList.value = []
    }
  } catch (err) {
    console.error('加载我的发布列表失败:', err)
    rawList.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadList()
})
</script>

<style scoped>
.my-published {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.mp-header {
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

.mp-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 6px;
  color: #303133;
  letter-spacing: -0.01em;
}

.mp-sub {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.mp-header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.btn-publish {
  background: linear-gradient(135deg, #42a5f5 0%, #1e88e5 100%);
  border: none;
  color: #ffffff !important;
  font-weight: 600;
  padding: 10px 24px;
  box-shadow: 0 4px 12px rgba(66, 165, 245, 0.3);
  transition: all 0.3s ease;
}

.btn-publish:hover {
  background: linear-gradient(135deg, #64b5f6 0%, #42a5f5 100%);
  box-shadow: 0 6px 20px rgba(66, 165, 245, 0.4);
  transform: translateY(-2px);
}

.btn-publish:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(66, 165, 245, 0.3);
}

.mp-header-actions :deep(.el-button:not(.btn-publish)) {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(66, 165, 245, 0.2);
  color: #42a5f5;
  font-weight: 500;
  transition: all 0.3s ease;
}

.mp-header-actions :deep(.el-button:not(.btn-publish):hover) {
  background: rgba(66, 165, 245, 0.1);
  border-color: #42a5f5;
  color: #1976d2;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 165, 245, 0.15);
}

/* 容器保持你的原样 */
.mp-toolbar {
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

/* 核心优化 1：使用 tabs 替换 */
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

.mp-search {
  width: 320px;
  margin-left: auto;
}

.mp-count {
  font-size: 13px;
  font-weight: 600;
  color: #909399;
}

.mp-skeleton {
  padding: 12px 0;
}

.waterfall {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  position: relative;
  z-index: 1;
}

@media (max-width: 1024px) {
  .waterfall {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .waterfall {
    grid-template-columns: 1fr;
  }
}

.mp-empty-wrap {
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

.mp-empty-wrap :deep(.el-empty__description) {
  color: #909399;
  font-weight: 500;
}
</style>
