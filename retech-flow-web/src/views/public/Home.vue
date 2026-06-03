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

    <!-- Features Section -->
    <section class="features-section">
      <div class="section-heading">
        <h2 class="section-title">把二手 3C 交易里最麻烦的事交给平台</h2>
        <p>估价、描述、审核、资金托管和纠纷处理连成一条链，卖家少折腾，买家更放心。</p>
      </div>
      <div class="features-grid reveal-stack">
        <article class="feature-card feature-card--blue">
          <div class="feature-icon-wrapper">
            <el-icon :size="30"><Aim /></el-icon>
          </div>
          <h3>AI 识别 + 行情估价</h3>
          <p>围绕品牌、型号、成色和市场热度生成参考价，减少卖家乱标价、买家反复砍价。</p>
        </article>

        <article class="feature-card feature-card--green">
          <div class="feature-icon-wrapper">
            <el-icon :size="30"><MagicStick /></el-icon>
          </div>
          <h3>详情自动生成</h3>
          <p>估价结果可直接带出标题、卖点和质检描述，发布商品不用从空白表单开始写。</p>
        </article>

        <article class="feature-card feature-card--orange">
          <div class="feature-icon-wrapper">
            <el-icon :size="30"><Lock /></el-icon>
          </div>
          <h3>审核与托管保障</h3>
          <p>商品先审核再上架，实名认证闭环，订单资金托管到平台，交易过程更可控。</p>
        </article>
      </div>
    </section>

    <!-- Market Section -->
    <section class="market-section">
      <div class="section-heading market-heading">
        <h2 class="section-title">严选在售 3C 好物</h2>
        <p>首页只露出重点货源，想慢慢挑可以进入交易广场按分类继续筛。</p>
      </div>
      
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

      <div class="products-grid" v-loading="loading">
        <GoodsCard 
          v-for="item in products" 
          :key="item.id" 
          :item="item"
          meta-type="views"
        />
      </div>

      <div class="more-actions">
        <el-button size="large" class="ghost-more-btn" @click="$router.push('/market')">
          进入交易广场 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </section>

    <!-- How it works -->
    <section class="steps-section">
      <div class="section-heading">
        <h2 class="section-title">从估价到到账，每一步都有状态可追</h2>
      </div>
      <div class="flow-list">
        <div class="flow-card">
          <div class="flow-index">01</div>
          <div class="flow-copy">
            <h3>拍照估价</h3>
            <p>上传照片获取AI报价</p>
          </div>
        </div>
        <div class="flow-card">
          <div class="flow-index">02</div>
          <div class="flow-copy">
            <h3>一键发布</h3>
            <p>确认价格后自动上架</p>
          </div>
        </div>
        <div class="flow-card">
          <div class="flow-index">03</div>
          <div class="flow-copy">
            <h3>买家下单</h3>
            <p>资金托管至平台</p>
          </div>
        </div>
        <div class="flow-card">
          <div class="flow-index">04</div>
          <div class="flow-copy">
            <h3>发货验机</h3>
            <p>买家确认收货</p>
          </div>
        </div>
        <div class="flow-card">
          <div class="flow-index">05</div>
          <div class="flow-copy">
            <h3>极速打款</h3>
            <p>交易完成秒到账</p>
          </div>
        </div>
      </div>
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
  padding-bottom: 72px;
  width: min(1120px, calc(100% - 48px));
  margin: 0 auto;
  padding-top: 20px;
}

.hero-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 80px 0 72px;
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
  overflow: hidden;
}

.hero-image img {
  max-width: 100%;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  opacity: 0;
  animation: heroImageSlideIn 0.86s cubic-bezier(0.22, 1, 0.36, 1) 0.18s forwards;
}

.section-heading {
  max-width: 720px;
  margin: 0 auto 34px;
  text-align: center;
}

.section-kicker {
  display: inline-flex;
  align-items: center;
  height: 26px;
  padding: 0 12px;
  border-radius: 999px;
  background: #eef5ff;
  color: #1d6fe8;
  font-size: 13px;
  font-weight: 700;
}

.section-title {
  margin: 14px 0 0;
  color: #273142;
  font-size: 30px;
  line-height: 1.35;
  font-weight: 800;
}

.section-heading p {
  margin: 14px auto 0;
  color: #667085;
  font-size: 15px;
  line-height: 1.8;
}

.features-section {
  padding: 36px 0 72px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.feature-card {
  min-height: 228px;
  padding: 24px;
  border: 1px solid #e8eef6;
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0 18px 48px rgba(31, 48, 79, 0.08);
  opacity: 0;
  transform: translateY(28px);
  animation: cardRise 0.62s ease forwards;
}

.feature-card:nth-child(2) {
  animation-delay: 0.12s;
}

.feature-card:nth-child(3) {
  animation-delay: 0.24s;
}

.feature-card:hover {
  border-color: #cfe0f5;
  transform: translateY(-4px);
  box-shadow: 0 22px 56px rgba(31, 48, 79, 0.12);
}

.feature-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 54px;
  height: 54px;
  margin-bottom: 22px;
  border-radius: 14px;
  color: #ffffff;
}

.feature-card--blue .feature-icon-wrapper {
  background: linear-gradient(135deg, #2f80ed, #56ccf2);
}

.feature-card--green .feature-icon-wrapper {
  background: linear-gradient(135deg, #12b886, #51cf66);
}

.feature-card--orange .feature-icon-wrapper {
  background: linear-gradient(135deg, #f59f00, #ff8787);
}

.feature-card h3 {
  margin: 0 0 12px;
  color: #1f2937;
  font-size: 20px;
  font-weight: 800;
}

.feature-card p {
  margin: 0;
  color: #667085;
  line-height: 1.75;
  font-size: 14px;
}

.market-section {
  padding: 56px 34px;
  border: 1px solid #e7edf5;
  border-radius: 22px;
  background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%);
}

.market-heading {
  margin-bottom: 24px;
}

.filter-tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.filter-tabs :deep(.el-radio-button__inner) {
  border-color: #d8e2ef;
  color: #536174;
  box-shadow: none;
}

.filter-tabs :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  border-color: #2f80ed;
  background: #2f80ed;
  color: #ffffff;
  box-shadow: none;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 22px 18px;
  width: 100%;
  min-height: 240px;
}

.more-actions {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

.ghost-more-btn {
  border-color: #cfd9e8;
  color: #273142;
  font-weight: 700;
}

.steps-section {
  padding: 86px 0 0;
}

.flow-list {
  position: relative;
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 18px;
}

.flow-card {
  position: relative;
  min-height: 178px;
  padding: 24px;
  border: 1px solid #e8eef6;
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0 18px 48px rgba(31, 48, 79, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

.flow-card:hover {
  border-color: #cfe0f5;
  transform: translateY(-4px);
  box-shadow: 0 22px 56px rgba(31, 48, 79, 0.12);
}

.flow-index {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 54px;
  height: 54px;
  margin-bottom: 22px;
  border-radius: 14px;
  background: linear-gradient(135deg, #2f80ed, #56ccf2);
  color: #ffffff;
  font-size: 18px;
  font-weight: 800;
}

.flow-copy {
  min-width: 0;
}

.flow-card h3 {
  margin: 0 0 12px;
  color: #1f2937;
  font-size: 18px;
  font-weight: 800;
}

.flow-card p {
  margin: 0;
  color: #667085;
  font-size: 14px;
  line-height: 1.75;
}

@keyframes cardRise {
  from {
    opacity: 0;
    transform: translateY(28px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes heroImageSlideIn {
  from {
    opacity: 0;
    transform: translateX(72px) scale(0.98);
  }

  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-image img {
    opacity: 1;
    animation: none;
  }
}

@media (max-width: 1024px) {
  .products-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .flow-list {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
  }

  .flow-card {
    border: 1px solid #e8eef6;
  }
}

@media (max-width: 820px) {
  .hero-section {
    flex-direction: column;
    align-items: flex-start;
    padding-top: 48px;
  }

  .hero-title {
    font-size: 38px;
  }

  .features-grid,
  .flow-list {
    grid-template-columns: 1fr;
  }

  .products-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .feature-card {
    min-height: auto;
  }

  .flow-card {
    min-height: auto;
    display: block;
    padding: 22px;
    border: 1px solid #e8eef6;
    background: #ffffff;
  }

  .flow-index {
    width: 50px;
    height: 50px;
    margin-bottom: 18px;
  }

  .market-section {
    padding: 42px 18px;
  }

  .flow-list {
    display: grid;
    padding: 0;
  }
}

@media (max-width: 560px) {
  .products-grid {
    grid-template-columns: 1fr;
  }
}
</style>
