<template>
  <div class="home-container">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="highlight">AI驱动</span> 的二手3C交易平台
        </h1>
        <p class="hero-subtitle">
          拍照自动估价 · 智能生成详情 · 极速变现 · 官方仲裁保障
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round class="cta-btn" @click="$router.push('/valuation')">
            立即免费估价
            <el-icon class="el-icon--right"><Camera /></el-icon>
          </el-button>
          <el-button size="large" round class="secondary-btn" @click="$router.push('/market')">
            浏览严选好货
          </el-button>
        </div>
      </div>
      <div class="hero-image">
        <!-- Placeholder for a 3C product illustration -->
        <img src="https://images.unsplash.com/photo-1550009158-9ebf69173e03?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80" alt="3C Devices" />
      </div>
    </section>

    <!-- Market Section -->
    <section class="market-section">
      <h2 class="section-title">交易广场</h2>
      
      <!-- 筛选 Tab -->
      <div class="filter-tabs">
        <el-radio-group v-model="activeCategory" size="large" @change="handleCategoryChange">
          <el-radio-button value="all">热门好物</el-radio-button>
          <el-radio-button 
            v-for="category in hotCategories" 
            :key="category.id" 
            :value="category.id"
          >
            {{ category.name }}
          </el-radio-button>
        </el-radio-group>
      </div>

      <!-- 商品网格 2*3 -->
      <div class="products-grid" v-loading="loading">
        <GoodsCard 
          v-for="item in products" 
          :key="item.id" 
          :item="item"
          meta-type="views"
        />
      </div>

      <!-- 查看更多 -->
      <div class="more-actions">
        <el-button size="large" @click="$router.push('/market')">
          查看更多好物 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <el-card class="feature-card" shadow="hover">
          <template #header>
            <div class="feature-icon-wrapper">
              <el-icon :size="40" color="#409eff"><Aim /></el-icon>
            </div>
          </template>
          <h3>智能视觉估价</h3>
          <p>上传实物照片，AI自动识别成色、划痕、屏幕状态，结合市场行情给出精准估价区间。</p>
        </el-card>

        <el-card class="feature-card" shadow="hover">
          <template #header>
            <div class="feature-icon-wrapper">
              <el-icon :size="40" color="#67c23a"><MagicStick /></el-icon>
            </div>
          </template>
          <h3>AIGC 一键发布</h3>
          <p>自动生成专业的商品标题和详细质检文案，告别繁琐的手动输入，秒级上架。</p>
        </el-card>

        <el-card class="feature-card" shadow="hover">
          <template #header>
            <div class="feature-icon-wrapper">
              <el-icon :size="40" color="#e6a23c"><Lock /></el-icon>
            </div>
          </template>
          <h3>安全交易保障</h3>
          <p>实名认证买卖双方，平台托管资金，更有专业的纠纷仲裁庭保障您的权益。</p>
        </el-card>
      </div>
    </section>

    <!-- How it works -->
    <section class="steps-section">
      <h2 class="section-title">交易流程</h2>
      <el-steps :active="1" align-center finish-status="success">
        <el-step title="拍照估价" description="上传照片获取AI报价" />
        <el-step title="一键发布" description="确认价格后自动上架" />
        <el-step title="买家下单" description="资金托管至平台" />
        <el-step title="发货验机" description="买家确认收货" />
        <el-step title="极速打款" description="交易完成秒到账" />
      </el-steps>
    </section>
  </div>
</template>

<script setup lang="ts">
import { Camera, Aim, MagicStick, Lock, ArrowRight } from '@element-plus/icons-vue'
import { ref, computed, onMounted } from 'vue'
import { useCategoryStore } from '@/store/categoryStore'
import goodsApi from '@/api/goodsapi'
import GoodsCard from '@/components/GoodsCard.vue'

const categoryStore = useCategoryStore()
const activeCategory = ref<number | 'all'>('all')
const loading = ref(false)
const products = ref<any[]>([])

// 仅展示热门分类：包含"手机"、"电脑"、"平板"的分类（如：智能手机、笔记本电脑等）
const hotKeywords = ['手机', '电脑', '平板']
const hotCategories = computed(() => {
  return categoryStore.categories.filter(c => 
    hotKeywords.some(keyword => c.name.includes(keyword))
  )
})

// 获取商品列表
const fetchGoodsList = async () => {
  loading.value = true
  try {
    const params: any = {}
    
    if (activeCategory.value !== 'all') {
      params.category_id = activeCategory.value
    } else {
      // 如果是“热门好物”，且热门分类已加载，将这几个分类的 ID 作为参数传给后端 (需后端支持)
      // 或者前端全量拉取后过滤。这里为简单起见，若选择全部，前端根据分类ID过滤
      // 更好做法是如果 activeCategory 是 all，且 hotCategories 有值，过滤掉非热门的商品
    }
    
    const res = await goodsApi.getGoodsListAPI(params)
    if (res.code === 200) {
      let dataList = Array.isArray(res.data) ? res.data : res.data?.list || res.data?.results || []
      
      // 如果当前是“热门好物(all)”Tab，我们在前端过滤出只属于这三个分类的商品
      if (activeCategory.value === 'all' && hotCategories.value.length > 0) {
        const hotIds = hotCategories.value.map(c => c.id)
        dataList = dataList.filter((item: any) => {
           const cid = item.category?.id || item.category_id
           return hotIds.includes(cid)
        })
      }
      
      // 首页只取前 8 个展示 (4x2 更美观)
      products.value = dataList.slice(0, 8)
    }
  } catch (error) {
    console.error('获取首页商品列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 切换分类
const handleCategoryChange = () => {
  fetchGoodsList()
}

onMounted(async () => {
  if (categoryStore.categories.length === 0) {
    await categoryStore.fetchCategories()
  }
  fetchGoodsList()
})
</script>

<style scoped>
.home-container {
  padding-bottom: 60px;
  width: 888px;
  margin: 0 auto;
  padding-top: 20px;
}

.hero-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 80px 0;
  gap: 40px;
}

.hero-content {
  flex: 1;
}

.hero-title {
  font-size: 48px;
  font-weight: 800;
  color: #303133;
  margin-bottom: 20px;
  line-height: 1.2;
}

.highlight {
  color: #409eff;
  position: relative;
}

.highlight::after {
  content: '';
  position: absolute;
  bottom: 5px;
  left: 0;
  width: 100%;
  height: 10px;
  background-color: rgba(64, 158, 255, 0.2);
  z-index: -1;
}

.hero-subtitle {
  font-size: 18px;
  color: #606266;
  margin-bottom: 40px;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 20px;
}

/* 立即免费估价按钮 - 炫彩流光呼吸灯效果 */
.cta-btn {
  position: relative;
  overflow: hidden;
  border: none !important;
  background-color: transparent !important;
  border-radius: 999px;
  animation: breatheShadow 3s ease-in-out infinite;
  z-index: 1;
}

/* 旋转的流光渐变层 */
.cta-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 300%;
  aspect-ratio: 1;
  /* 极光蓝、量子紫、青色交替的圆锥渐变 */
  background: conic-gradient(
    #3b82f6, 
    #8b5cf6, 
    #00ffff, 
    #3b82f6
  );
  animation: rotateGlow 4s linear infinite;
  z-index: -2;
  transform-origin: center;
}

/* 内部裁切层 (使用 inset 留出 2px 边缘) */
.cta-btn::after {
  content: '';
  position: absolute;
  inset: 2px;
  background-color: #409eff; /* 按钮内部底色 */
  border-radius: 999px;
  z-index: -1;
  transition: background-color 0.3s;
}

/* 保证文字和图标显示在最上层 */
.cta-btn :deep(span), .cta-btn :deep(i) {
  position: relative;
  z-index: 2;
  color: #fff;
}

/* 悬停状态：流光加速，阴影发光增强，内部颜色微调 */
.cta-btn:hover::before {
  animation: rotateGlow 1.5s linear infinite;
}

.cta-btn:hover {
  animation: breatheShadowHover 1.5s ease-in-out infinite;
}

.cta-btn:hover::after {
  background-color: #79bbff;
}

@keyframes rotateGlow {
  0% { transform: translate(-50%, -50%) rotate(0deg); }
  100% { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes breatheShadow {
  0%, 100% { box-shadow: 0 0 10px rgba(139, 92, 246, 0.4); }
  50% { box-shadow: 0 0 20px rgba(139, 92, 246, 0.8); }
}

@keyframes breatheShadowHover {
  0%, 100% { box-shadow: 0 0 15px rgba(139, 92, 246, 0.6); }
  50% { box-shadow: 0 0 30px rgba(139, 92, 246, 1); }
}

.hero-image {
  flex: 1;
  display: flex;
  justify-content: center;
}

.hero-image img {
  max-width: 100%;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.market-section {
  padding: 80px 0;
  background-color: #f9fafc;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.filter-tabs {
  margin-bottom: 40px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* 改为 4 列更宽阔美观 */
  gap: 24px 20px; /* 行间距稍微调大，列间距适中 */
  max-width: 1200px;
  width: 100%;
  margin-bottom: 40px;
}

.product-card {
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.product-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
}

.product-info {
  padding: 15px;
}

.product-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #303133;
  /* 文本截断 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.product-price {
  font-size: 18px;
  color: #f56c6c;
  font-weight: bold;
}

.product-condition {
  font-size: 12px;
  color: #909399;
  background-color: #f4f4f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.product-tags {
  display: flex;
  gap: 5px;
}

.more-actions {
  margin-top: 20px;
}

.section-title {
  text-align: center;
  font-size: 32px;
  color: #303133;
  margin-bottom: 60px;
  font-weight: 700;
}

.features-section {
  padding: 80px 0;
  background-color: #fff;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}

.feature-card {
  text-align: center;
  border: none;
  background-color: #f9fafc;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-10px);
}

.feature-icon-wrapper {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-card h3 {
  font-size: 20px;
  color: #303133;
  margin-bottom: 15px;
}

.feature-card p {
  color: #909399;
  line-height: 1.6;
}

.steps-section {
  padding: 80px 0;
}
</style>
