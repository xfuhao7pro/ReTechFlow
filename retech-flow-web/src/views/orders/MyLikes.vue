<template>
  <DecorativeBackground>
    <div class="my-likes">
      <header class="ml-header">
        <div class="ml-header-text">
          <h1 class="ml-title">我的收藏</h1>
          <p class="ml-sub">查看你收藏的所有商品</p>
        </div>
      </header>

      <div class="ml-toolbar">
        <div class="ml-search">
          <SearchBox
            v-model="searchKeyword"
            placeholder="搜索收藏的商品"
            @search="handleSearch"
          />
        </div>
        <span class="ml-count">共 {{ displayList.length }} 件</span>
      </div>

      <el-skeleton v-if="loading" :rows="6" animated class="ml-skeleton" />

      <template v-else-if="displayList.length">
        <div class="waterfall" role="list">
          <GoodsCard
            v-for="item in displayList"
            :key="item.id"
            :item="item"
            :show-status="true"
            meta-type="views"
          >
            <template #extra>
              <div class="wf-like-time">
                <el-icon><Clock /></el-icon>
                <span>{{ formatTime(item.created_at) }} 收藏</span>
              </div>
            </template>
          </GoodsCard>
        </div>
      </template>

      <div v-else class="ml-empty-wrap">
        <el-empty description="还没有收藏任何商品">
          <el-button type="primary" round @click="router.push('/market')">
            <el-icon class="el-icon--left"><ShoppingBag /></el-icon>
            去逛逛
          </el-button>
        </el-empty>
      </div>
    </div>
  </DecorativeBackground>
</template>

<script lang="ts" setup name="MyLikes">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ShoppingBag, Clock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import goodsApi from '@/api/goodsapi'
import GoodsCard from '@/components/GoodsCard.vue'
import DecorativeBackground from '@/components/DecorativeBackground.vue'
import SearchBox from '@/components/SearchBox.vue'
import { formatTime } from '@/utils/format'

const router = useRouter()

const loading = ref(true)
const rawList = ref<any[]>([])
const searchKeyword = ref('')

const displayList = computed(() => {
  if (!searchKeyword.value.trim()) {
    return rawList.value
  }
  const kw = searchKeyword.value.toLowerCase()
  return rawList.value.filter(item =>
    item.title.toLowerCase().includes(kw)
  )
})

function handleSearch() {
}

async function loadList() {
  loading.value = true
  try {
    const res = await goodsApi.getMyLikesAPI()

    if (res.code === 200 && res.data) {
      const list = Array.isArray(res.data) ? res.data : (res.data.list || [])

      rawList.value = list.map((item: any) => {
        return {
          id: item.id,
          title: item.title,
          price: item.price,
          cover: item.images?.[0]?.image || '', // GoodsCard会处理
          status: item.status,
          views: item.views || 0,
          created_at: item.created_at
        }
      })
    } else {
      ElMessage.error(res.msg || '加载失败')
    }
  } catch (err) {
    console.error('加载收藏列表失败:', err)
    ElMessage.error('加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadList()
})
</script>

<style scoped>
.my-likes {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.ml-header {
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

.ml-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 6px;
  color: #303133;
  letter-spacing: -0.01em;
}

.ml-sub {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.ml-toolbar {
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

.ml-search {
  width: 320px;
}

.ml-count {
  font-size: 13px;
  font-weight: 600;
  color: #909399;
}

.ml-skeleton {
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

.wf-like-time {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  font-size: 12px;
  color: #c0c4cc;
}

.wf-like-time .el-icon {
  font-size: 14px;
}

.ml-empty-wrap {
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

.ml-empty-wrap :deep(.el-empty__description) {
  color: #909399;
  font-weight: 500;
}
</style>
