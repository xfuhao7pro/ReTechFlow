<template>
  <DecorativeBackground>
    <div class="square-page">
      <div class="square-container">
        <!-- 头部与搜索区 -->
        <header class="sq-header">
          <div class="sq-header-text">
            <h1 class="sq-title">交易广场</h1>
            <p class="sq-sub">发现海量严选好物，总有一款适合你</p>
          </div>
          <div class="sq-search-box">
            <SearchBox
              v-model="queryParams.keyword"
              placeholder="搜索你想要的商品..."
              @search="handleSearch"
            />
          </div>
        </header>

        <!-- 筛选区 -->
        <div class="sq-filter-section">
          <!-- 分类筛选 -->
          <div class="filter-row">
            <div class="filter-label">分类：</div>
            <div class="filter-options">
              <span
                class="filter-tag"
                :class="{ active: !queryParams.category_id }"
                @click="handleCategoryChange(undefined)"
              >
                全部
              </span>
              <span
                v-for="cat in categoryStore.categories"
                :key="cat.id"
                class="filter-tag"
                :class="{ active: queryParams.category_id === cat.id }"
                @click="handleCategoryChange(cat.id)"
              >
                {{ cat.name }}
              </span>
            </div>
          </div>

          <!-- 动态属性筛选 (仅当选中具体分类时显示) -->
          <template v-if="currentCategory && currentCategory.attributes">
            <div
              v-for="(attr, idx) in currentCategory.attributes"
              :key="idx"
              class="filter-row"
            >
              <div class="filter-label">{{ attr.name }}：</div>
              <div class="filter-options">
                <span
                  class="filter-tag"
                  :class="{ active: !queryParams.attributes[attr.name] }"
                  @click="handleAttributeChange(attr.name, undefined)"
                >
                  全部
                </span>
                <span
                  v-for="opt in attr.options"
                  :key="opt"
                  class="filter-tag"
                  :class="{ active: queryParams.attributes[attr.name] === opt }"
                  @click="handleAttributeChange(attr.name, opt)"
                >
                  {{ opt }}
                </span>
              </div>
            </div>
          </template>
        </div>

        <!-- 商品列表 -->
        <div class="sq-content">
          <el-skeleton v-if="loading" :rows="8" animated class="sq-skeleton" />

          <template v-else>
            <div v-if="goodsList.length > 0" class="waterfall">
              <GoodsCard
                v-for="item in goodsList"
                :key="item.id"
                :item="item"
                meta-type="wants"
              />
            </div>

            <!-- 空状态 -->
            <div v-else class="sq-empty-wrap">
              <el-empty
                description="没有找到符合条件的商品，换个关键词试试吧"
                :image-size="160"
              />
            </div>
          </template>
        </div>
      </div>
    </div>
  </DecorativeBackground>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { useCategoryStore } from "@/store/categoryStore";
import goodsApi from "@/api/goodsapi";
import { ElMessage } from "element-plus";
import GoodsCard from "@/components/GoodsCard.vue";
import DecorativeBackground from "@/components/DecorativeBackground.vue";
import SearchBox from "@/components/SearchBox.vue";

const categoryStore = useCategoryStore();

const loading = ref(false);
const goodsList = ref<any[]>([]);

// 搜索和筛选参数
const queryParams = reactive({
  keyword: "",
  category_id: undefined as number | undefined,
  attributes: {} as Record<string, string | undefined>,
});

// 当前选中的分类
const currentCategory = computed(() => {
  if (!queryParams.category_id) return null;
  return categoryStore.categories.find((c) => c.id === queryParams.category_id);
});

// 切换分类
const handleCategoryChange = (catId?: number) => {
  queryParams.category_id = catId;
  // 切换分类时清空已选属性
  queryParams.attributes = {};
  handleSearch();
};

// 切换属性
const handleAttributeChange = (attrName: string, value?: string) => {
  queryParams.attributes[attrName] = value;
  handleSearch();
};

// 执行搜索
const handleSearch = async () => {
  loading.value = true;
  try {
    // 构造请求参数
    const params: any = {
      keyword: queryParams.keyword || undefined,
      category_id: queryParams.category_id || undefined,
    };

    // 将选中的属性加入参数 (如果有值的话)
    Object.keys(queryParams.attributes).forEach((key) => {
      const val = queryParams.attributes[key];
      if (val) {
        params[`attr_${key}`] = val; // 假设后端使用 attr_ 前缀接收属性筛选
      }
    });

    const res = await goodsApi.getGoodsListAPI(params);
    if (res.code === 200) {
      // 1. 先拿到原始数组
      goodsList.value = Array.isArray(res.data)
        ? res.data
        : res.data?.list || res.data?.results || [];
    } else {
      ElMessage.error(res.msg || "获取商品列表失败");
    }
  } catch (error) {
    console.error("Failed to fetch goods:", error);
    ElMessage.error("获取商品列表失败，请稍后重试");
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  // 确保分类数据已加载
  if (categoryStore.categories.length === 0) {
    await categoryStore.fetchCategories();
  }
  handleSearch();
});
</script>

<style scoped>
.square-page {
  min-height: 100vh;
  padding: 32px 0;
}

.square-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  position: relative;
  z-index: 1;
}

/* 头部区 */
.sq-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 20px;
}

.sq-header-text {
  flex-shrink: 0;
}

.sq-title {
  font-size: 32px;
  font-weight: 800;
  margin: 0 0 8px;
  color: #303133;
  letter-spacing: -0.01em;
}

.sq-sub {
  margin: 0;
  font-size: 15px;
  color: #909399;
}

/* 搜索框 */
.sq-search-box {
  width: 480px;
  max-width: 100%;
}

/* 筛选区 */
.sq-filter-section {
  background: #ffffff;
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  border: 1px solid #f0f0f0;
}

.filter-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-label {
  width: 70px;
  flex-shrink: 0;
  font-size: 14px;
  color: #909399;
  font-weight: 500;
  line-height: 32px;
}

.filter-options {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-tag {
  display: inline-block;
  padding: 0 16px;
  height: 32px;
  line-height: 32px;
  border-radius: 16px;
  font-size: 14px;
  color: #606266;
  background: #f5f7fa;
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
}

.filter-tag:hover {
  color: #409eff;
  background: #ecf5ff;
}

.filter-tag.active {
  background: #409eff;
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

/* 瀑布流展示区 - 5列 */
.waterfall {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
}

@media (max-width: 1400px) {
  .waterfall {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1100px) {
  .waterfall {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 800px) {
  .waterfall {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 500px) {
  .waterfall {
    grid-template-columns: 1fr;
  }
}

/* 空状态 */
.sq-empty-wrap {
  padding: 60px 0;
  background: #ffffff;
  border-radius: 16px;
  border: 1px dashed #e4e7ed;
}

.sq-skeleton {
  padding: 20px;
  background: #fff;
  border-radius: 12px;
}
</style>
