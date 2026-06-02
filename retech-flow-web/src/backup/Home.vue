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
        <el-radio-group v-model="activeCategory" size="large">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="phone">手机</el-radio-button>
          <el-radio-button label="laptop">笔记本</el-radio-button>
          <el-radio-button label="camera">相机</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 商品网格 2*3 -->
      <div class="products-grid">
        <el-card 
          v-for="item in displayProducts" 
          :key="item.id" 
          class="product-card" 
          :body-style="{ padding: '0px' }"
          shadow="hover"
        >
          <img :src="item.image" class="product-image" />
          <div class="product-info">
            <h3 class="product-title">{{ item.title }}</h3>
            <div class="product-meta">
              <span class="product-price">¥{{ item.price }}</span>
              <span class="product-condition">{{ item.condition }}成新</span>
            </div>
            <div class="product-tags">
              <el-tag size="small" effect="plain" v-for="tag in item.tags" :key="tag">{{ tag }}</el-tag>
            </div>
          </div>
        </el-card>
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
import { ref, computed } from 'vue'

const activeCategory = ref('all')

// 模拟商品数据 (2x3 = 6个)
const products = [
  { id: 1, title: 'iPhone 13 Pro Max 256G 远峰蓝', price: 5200, condition: 95, category: 'phone', tags: ['国行', '无拆修'], image: 'https://images.unsplash.com/photo-1632661674596-df8be070a5c5?auto=format&fit=crop&w=400&q=80' },
  { id: 2, title: 'MacBook Pro 14 M1 Pro 16+512', price: 8500, condition: 98, category: 'laptop', tags: ['带AC+', '充新'], image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca4?auto=format&fit=crop&w=400&q=80' },
  { id: 3, title: 'Sony A7M4 单机身', price: 13800, condition: 99, category: 'camera', tags: ['箱说全', '快门200'], image: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=400&q=80' },
  { id: 4, title: 'iPad Air 5 64G WiFi 紫色', price: 3100, condition: 95, category: 'phone', tags: ['在保', '送笔'], image: 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=400&q=80' },
  { id: 5, title: 'Dell XPS 13 Plus i7/16G', price: 6800, condition: 90, category: 'laptop', tags: ['轻薄本', '高分屏'], image: 'https://images.unsplash.com/photo-1593642632823-8f78536788c6?auto=format&fit=crop&w=400&q=80' },
  { id: 6, title: 'Fujifilm X100V 黑色', price: 9200, condition: 95, category: 'camera', tags: ['网红机', '扫街'], image: 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?auto=format&fit=crop&w=400&q=80' },
]

const displayProducts = computed(() => {
  if (activeCategory.value === 'all') {
    return products.slice(0, 6)
  }
  // 实际项目中这里可能需要重新调接口或者从更多数据中筛选
  // 这里为了演示 2x3 布局，模拟数据量可能不足 6 个，实际展示所有匹配项即可
  return products.filter(p => p.category === activeCategory.value).slice(0, 6)
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
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
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
