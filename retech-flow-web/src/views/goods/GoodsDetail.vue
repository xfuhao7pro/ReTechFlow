<template>
  <div class="goods-detail-page">
    <el-skeleton v-if="loading" :rows="8" animated />

    <template v-else-if="goods">
      <div class="detail-container">
        <div class="thumbnail-gallery">
          <div
            v-for="(img, idx) in goods.images"
            :key="idx"
            class="thumbnail-item"
            :class="{ active: currentImageIndex === idx }"
            @click="currentImageIndex = Number(idx)"
          >
            <el-image :src="img" fit="cover" />
          </div>
        </div>

        <div class="main-image-section">
          <div class="image-wrapper">
            <div
              class="nav-btn prev-btn"
              :class="{ disabled: currentImageIndex === 0 }"
              @click="prevImage"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
            </div>

            <el-image
              :src="goods.images[currentImageIndex]"
              fit="contain"
              class="main-image"
              :preview-src-list="goods.images"
              :initial-index="currentImageIndex"
            />

            <div
              class="nav-btn next-btn"
              :class="{ disabled: currentImageIndex === goods.images.length - 1 }"
              @click="nextImage"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
          </div>

          <div class="image-indicator">
            {{ currentImageIndex + 1 }} / {{ goods.images.length }}
          </div>
        </div>

        <div class="info-section">
          <div class="info-header">
            <h1 class="goods-title">{{ goods.title }}</h1>
            <div class="price-row">
              <div class="price-left">
                <span class="price-label">价格</span>
                <span class="price-value">¥{{ formatPrice(goods.price) }}</span>
              </div>
              <!-- 成色标签 -->
              <div class="condition-badge" v-if="conditionText">
                <span class="condition-text">{{ conditionText }}</span>
                <span class="condition-highlight"></span>
              </div>
            </div>
          </div>

          <!-- 卖家信息卡片 -->
          <div class="seller-card">
            <div class="seller-info">
              <el-avatar :size="50" :src="goods.seller?.avatar ? getImageUrl(goods.seller.avatar) : 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'">
                {{ formatSellerName(goods.seller?.nickname || goods.seller?.username) }}
              </el-avatar>
              <div class="seller-details">
                <div class="seller-name">{{ formatSellerName(goods.seller?.nickname || goods.seller?.username) }}</div>
                <div class="seller-meta">
                  <el-icon><View /></el-icon>
                  <span>{{ goods.views || 0 }} 浏览</span>
                </div>
              </div>
            </div>
            <el-button type="primary" plain class="contact-btn" @click="handleContactSeller">联系卖家</el-button>
          </div>

          <!-- 商品描述 (在属性上面) -->
          <div class="goods-description" v-if="goods.description">
            <h3 class="section-title">商品描述</h3>
            <p class="description-text">{{ goods.description }}</p>
          </div>

          <el-divider />

          <!-- 商品属性 (两列布局, 排除成色) -->
          <div class="goods-attributes" v-if="filteredAttributes && Object.keys(filteredAttributes).length > 0">
            <h3 class="section-title">商品属性</h3>
            <div class="attr-grid">
              <div v-for="(value, key) in filteredAttributes" :key="key" class="attr-item">
                <span class="attr-label">{{ key }}</span>
                <span class="attr-value">{{ value }}</span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 (在属性下面) -->
          <div class="action-buttons">
            <el-button type="primary" size="large" class="buy-btn" @click="handleBuy">
              <el-icon><ShoppingCart /></el-icon>
              立即购买
            </el-button>
            <el-button size="large" class="chat-btn" @click="handleContactSeller">
              <el-icon><ChatDotRound /></el-icon>
              聊一聊
            </el-button>
            <el-button
              size="large"
              circle
              class="favorite-btn"
              :class="{ 'is-liked': goods.is_like }"
              :loading="likeLoading"
              @click="toggleLike"
            >
              <el-icon v-if="goods.is_like" color="#f56c6c"><svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M512 896a32 32 0 0 1-22.656-9.344l-339.2-339.2c-73.664-73.664-73.664-192.512 0-266.176s192.512-73.664 266.176 0L512 376.832l95.68-95.552c73.664-73.664 192.512-73.664 266.176 0s73.664 192.512 0 266.176l-339.2 339.2A32 32 0 0 1 512 896z"></path></svg></el-icon>
              <el-icon v-else><svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M512 896a32 32 0 0 1-22.656-9.344l-339.2-339.2c-73.664-73.664-73.664-192.512 0-266.176s192.512-73.664 266.176 0L512 376.832l95.68-95.552c73.664-73.664 192.512-73.664 266.176 0s73.664 192.512 0 266.176l-339.2 339.2A32 32 0 0 1 512 896zm-293.952-569.152c-48.64 48.64-48.64 127.36 0 176l293.952 293.952 293.952-293.952c48.64-48.64 48.64-127.36 0-176s-127.36-48.64-176 0L534.656 422.4a32 32 0 0 1-45.312 0L394.048 326.848c-48.64-48.64-127.36-48.64-176 0z"></path></svg></el-icon>
            </el-button>
          </div>
        </div>
      </div>

      <!-- 其他类似好物 -->
      <div class="similar-section" v-if="similarGoods.length > 0">
        <div class="similar-header">
          <h2 class="similar-title">其他类似好物</h2>
          <span class="similar-category" v-if="goods.category?.name">{{ goods.category.name }}</span>
        </div>
        <div class="similar-waterfall">
          <GoodsCard
            v-for="item in similarGoods"
            :key="item.id"
            :item="item"
            meta-type="wants"
          />
        </div>
      </div>
    </template>

    <el-empty v-else description="商品不存在" />

    <!-- 下单确认弹窗 -->
    <el-dialog 
      v-model="checkoutVisible" 
      title="确认下单" 
      width="520px"
      custom-class="checkout-dialog"
      destroy-on-close
    >
      <div class="checkout-content" v-loading="addressLoading">
        <!-- 1. 商品信息卡片 -->
        <div class="checkout-goods-card" v-if="goods">
          <el-image 
            class="goods-cover" 
            :src="goods.images?.[0] || ''" 
            fit="cover" 
          />
          <div class="goods-info">
            <div class="goods-title">{{ goods.title }}</div>
            <div class="goods-price-row">
              <span class="price">¥{{ formatPrice(goods.price) }}</span>
            </div>
          </div>
        </div>

        <!-- 2. 收货地址选择 -->
        <div class="checkout-section">
          <div class="section-header">
            <span class="title">收货地址</span>
          </div>
          
          <div class="address-selector" v-if="addressList.length > 0">
            <div 
              class="address-item" 
              :class="{ 'is-selected': selectedAddressId === addr.id }"
              v-for="addr in addressList" 
              :key="addr.id"
              @click="selectAddress(addr)"
            >
              <div class="address-main">
                <div class="contact-info">
                  <span class="name">{{ addr.receiver_name }}</span>
                  <span class="phone">{{ addr.telephone }}</span>
                  <el-tag size="small" type="danger" v-if="addr.is_default">默认</el-tag>
                </div>
                <div class="address-detail">
                  {{ addr.province }}{{ addr.city }}{{ addr.district }}{{ addr.detail_address }}
                </div>
              </div>
              <el-icon class="check-icon" v-show="selectedAddressId === addr.id"><Select /></el-icon>
            </div>
          </div>
          
          <div v-else class="empty-address">
            <el-empty :image-size="60" description="暂无收货地址" />
            <el-button type="primary" link @click="router.push('/orders/address')">去添加地址</el-button>
          </div>
        </div>

        <!-- 3. 发货方式 & 支付方式 -->
        <div class="checkout-section">
          <div class="info-row">
            <span class="label">发货方式</span>
            <span class="value">{{ deliveryMethodText }}</span>
          </div>
          <div class="info-row">
            <span class="label">支付方式</span>
            <span class="value pay-method">
              <el-icon color="#409EFF"><Wallet /></el-icon> 余额支付
            </span>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="checkout-footer">
          <div class="total-price">
            共计：<span class="price">¥{{ formatPrice(goods?.price || 0) }}</span>
          </div>
          <div class="actions">
            <el-button @click="checkoutVisible = false">取消</el-button>
            <el-button 
              type="primary" 
              @click="submitOrder" 
              :loading="submitLoading"
              :disabled="!selectedAddressId"
            >
              确认支付
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View, ShoppingCart, ChatDotRound, Select, Wallet } from '@element-plus/icons-vue'
import goodsApi from '@/api/goodsapi'
import chatApi from '@/api/chatapi'
import userApi from '@/api/userapi'
import ordersApi from '@/api/ordersapi'
import { getImageUrl, formatPrice } from '@/utils/format'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/userstore'
import GoodsCard from '@/components/GoodsCard.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(true)
const goods = ref<any>(null)
const currentImageIndex = ref(0)
const likeLoading = ref(false)
const similarGoods = ref<any[]>([])

const checkoutVisible = ref(false)
const submitLoading = ref(false)
const addressLoading = ref(false)
const addressList = ref<any[]>([])
const selectedAddressId = ref<number | null>(null)

// 从属性中提取成色
const conditionText = computed(() => {
  if (!goods.value?.attributes) return ''
  return goods.value.attributes['成色'] || ''
})

// 提取发货方式
const deliveryMethodText = computed(() => {
  if (!goods.value?.attributes) return '快递发货'
  return goods.value.attributes['发货方式'] || '快递发货'
})

// 过滤掉成色后的属性 (成色已在价格旁边展示)
const filteredAttributes = computed(() => {
  if (!goods.value?.attributes) return {}
  const attrs = { ...goods.value.attributes }
  delete attrs['成色']
  return attrs
})

const prevImage = () => {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
  }
}

const nextImage = () => {
  if (currentImageIndex.value < goods.value.images.length - 1) {
    currentImageIndex.value++
  }
}

const formatSellerName = (name: string | undefined) => {
  if (!name) return '神秘用户'
  if (name.length <= 2) {
    return name.substring(0, 1) + '*'
  }
  return name.substring(0, 2) + '***' + name.substring(name.length - 1)
}

async function loadGoodsDetail() {
  loading.value = true
  try {
    const goodsId = route.params.id as string
    const res = await goodsApi.getGoodsDetailAPI(goodsId)

    if (res.code === 200 && res.data) {
      const data = res.data

      const images = data.images?.map((img: any) => {
        const imgPath = typeof img === 'string' ? img : img.image
        return getImageUrl(imgPath)
      }) || []

      goods.value = {
        id: data.id,
        title: data.title,
        price: data.price,
        description: data.description,
        images: images,
        seller: data.seller,
        category: data.category,
        attributes: data.attributes || {},
        status: data.status,
        views: data.views || 0,
        created_at: data.created_at,
        is_like: data.is_like || false
      }

      // 加载同类商品
      if (data.category?.id) {
        loadSimilarGoods(data.category.id, data.id)
      } else if (data.category_id) {
        loadSimilarGoods(data.category_id, data.id)
      }
    }
  } catch (err) {
    ElMessage.error('加载商品详情失败')
  } finally {
    loading.value = false
  }
}

async function loadSimilarGoods(categoryId: number, excludeId: string) {
  try {
    const res = await goodsApi.getGoodsListAPI({ category_id: categoryId })
    if (res.code === 200) {
      // 兼容 Django 后端的不同分页结构
      let list = []
      if (Array.isArray(res.data)) {
        list = res.data
      } else if (res.data?.list) {
        list = res.data.list
      } else if (res.data?.results) {
        list = res.data.results
      }
      
      // 排除当前商品
      similarGoods.value = list.filter((item: any) => String(item.id) !== String(excludeId)).slice(0, 10)
    }
  } catch (err) {
    console.error('加载类似商品失败:', err)
  }
}

async function toggleLike() {
  if (!goods.value) return

  likeLoading.value = true
  try {
    const res = await goodsApi.toggleLikeAPI({ goods_id: goods.value.id })

    if (res.code === 200 && res.data) {
      goods.value.is_like = res.data.is_like
      ElMessage.success(res.msg || (res.data.is_like ? '收藏成功' : '取消收藏'))
    } else {
      ElMessage.error(res.msg || '操作失败')
    }
  } catch (err) {
    console.error('切换收藏状态失败:', err)
    ElMessage.error('操作失败，请稍后重试')
  } finally {
    likeLoading.value = false
  }
}

async function handleContactSeller() {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再联系卖家')
    router.push('/login')
    return
  }
  if (!goods.value || !goods.value.seller) {
    ElMessage.error('无法获取卖家信息')
    return
  }
  if (goods.value.seller.id === userStore.userId) {
    ElMessage.warning('这是您自己发布的商品')
    return
  }
  try {
    const res = await chatApi.createSessionAPI({
      goods_id: goods.value.id,
      receiver_id: goods.value.seller.id
    })
    if (res.code === 200 && res.data?.session_id) {
      router.push(`/orders/messages?sessionId=${res.data.session_id}`)
    } else {
      ElMessage.error(res.msg || '发起聊天失败')
    }
  } catch (err) {
    console.error('发起聊天异常:', err)
  }
}

const handleBuy = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录！')
    router.push('/login')
    return
  }
  if (goods.value?.seller?.id === userStore.userId) {
    ElMessage.warning('不能购买自己发布的商品！')
    return
  }

  checkoutVisible.value = true
  addressLoading.value = true
  // 拉取地址列表
  try {
    const res = await userApi.getAddressListAPI()
    if (res.code === 200 && res.data) {
      addressList.value = res.data
      if (res.data.length > 0) {
        const defaultAddr = res.data.find((addr: any) => addr.is_default) || res.data[0]
        selectedAddressId.value = defaultAddr?.id ?? null
      }
    }
  } catch (e) {
    console.error('Failed to load addresses:', e)
  } finally {
    addressLoading.value = false
  }
}

const selectAddress = (addr: any) => {
  selectedAddressId.value = addr.id
}

const submitOrder = async () => {
  if (!selectedAddressId.value) {
    ElMessage.warning('请选择收货地址')
    return
  }

  const selectedAddr = addressList.value.find(a => a.id === selectedAddressId.value)
  if (!selectedAddr) return

  submitLoading.value = true
  try {
    const orderRes = await ordersApi.createOrder({
      goods_id: goods.value.id,
      receiver_name: selectedAddr.receiver_name,
      receiver_phone: selectedAddr.telephone,
      receiver_address: `${selectedAddr.province}${selectedAddr.city}${selectedAddr.district}${selectedAddr.detail_address}`
    })
    if (orderRes.code === 200) {
      // 订单创建成功，立即发起支付
      const payRes = await ordersApi.payOrder(orderRes.data.order_id)
      if (payRes.code === 200) {
        ElMessage.success('支付成功！')
        checkoutVisible.value = false
        router.push('/orders/bought')
      } else {
        ElMessage.error(payRes.msg || '支付失败，可在订单列表继续支付')
        checkoutVisible.value = false
        router.push('/orders/bought')
      }
    } else {
      ElMessage.error(orderRes.msg || '下单失败')
    }
  } catch (e: any) {
    console.error(e)
    // 提取可能在 e.response 里的报错信息
    const msg = e.response?.data?.msg || '操作失败'
    ElMessage.error(msg)
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  loadGoodsDetail()
})
</script>

<style scoped lang="scss">
.goods-detail-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px;
}

.detail-container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  padding: 30px;
  display: flex;
  gap: 30px;
}

.thumbnail-gallery {
  width: 80px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.thumbnail-item {
  width: 80px;
  height: 80px;
  border: 2px solid transparent;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    border-color: #409eff;
  }

  &.active {
    border-color: #409eff;
    box-shadow: 0 0 8px rgba(64, 158, 255, 0.3);
  }

  .el-image {
    width: 100%;
    height: 100%;
  }
}

.main-image-section {
  flex-shrink: 0;
  width: 480px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.image-wrapper {
  position: relative;
  width: 100%;
  height: 480px;
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
}

.main-image {
  display: block !important;
  width: 100%;
  height: 100%;
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s, opacity 0.25s;
  color: #333;
  opacity: 0;

  svg {
    width: 14px;
    height: 14px;
  }

  &:hover {
    background: #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
  }

  &.disabled {
    display: none;
  }

  &.prev-btn {
    left: 8px;
  }

  &.next-btn {
    right: 8px;
  }
}

.image-wrapper:hover .nav-btn:not(.disabled) {
  opacity: 1;
}

.image-indicator {
  margin-top: 15px;
  color: #666;
  font-size: 14px;
}

.info-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.info-header {
  margin-bottom: 20px;
}

.goods-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0 0 15px 0;
  line-height: 1.4;
}

.price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.price-left {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.price-label {
  font-size: 14px;
  color: #666;
}

.price-value {
  font-size: 32px;
  font-weight: 700;
  color: #ff4d4f;
}

// 成色标签 - 黄色荧光笔下划线风格
.condition-badge {
  position: relative;
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
  padding: 4px 0;
}

.condition-text {
  position: relative;
  z-index: 1;
  font-size: 20px;
  font-weight: 800;
  color: #1a1a1a;
  letter-spacing: 2px;
}

.condition-highlight {
  position: absolute;
  left: -2px;
  right: -2px;
  bottom: 4px;
  height: 10px;
  background: #ffd234;
  border-radius: 2px;
  z-index: 0;
}

.seller-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.seller-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.seller-details {
  flex: 1;
}

.seller-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
}

.seller-meta {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #999;
}

// 商品描述
.goods-description {
  margin-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 15px 0;
}

.description-text {
  font-size: 14px;
  color: #666;
  line-height: 1.8;
  white-space: pre-wrap;
  margin: 0;
}

// 商品属性 - 两列布局
.goods-attributes {
  margin-bottom: 20px;
}

.attr-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 24px;
}

.attr-item {
  display: flex;
  font-size: 14px;
  line-height: 1.6;
  background: #f8f9fa;
  padding: 8px 12px;
  border-radius: 6px;
}

.attr-label {
  color: #999;
  min-width: 56px;
  flex-shrink: 0;

  &::after {
    content: '：';
  }
}

.attr-value {
  color: #333;
  font-weight: 500;
  flex: 1;
}

// 操作按钮
.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.buy-btn {
  flex: 1;
}

.chat-btn {
  flex: 1;
}

.favorite-btn {
  flex-shrink: 0;
  border-color: #dcdfe6;
  color: #606266;
  transition: all 0.3s;
  
  &:hover {
    color: #f56c6c;
    border-color: #fbc4c4;
    background-color: #fef0f0;
  }
  
  &.is-liked {
    border-color: #f56c6c;
    background-color: #fef0f0;
    
    &:hover {
      background-color: #f56c6c;
      color: #fff;
      
      .el-icon {
        color: #fff !important;
      }
    }
  }
}

// 类似好物区域
.similar-section {
  max-width: 1200px;
  margin: 32px auto 0;
}

.similar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.similar-title {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
  margin: 0;
}

.similar-category {
  display: inline-block;
  padding: 2px 14px;
  background: linear-gradient(135deg, #e0f0ff, #c7e2ff);
  color: #3b82c4;
  font-size: 14px;
  font-weight: 600;
  border-radius: 12px;
}

.similar-waterfall {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
}

@media (max-width: 1400px) {
  .similar-waterfall {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1100px) {
  .similar-waterfall {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 800px) {
  .similar-waterfall {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1200px) {
  .detail-container {
    flex-wrap: wrap;
  }

  .thumbnail-gallery {
    flex-direction: row;
    flex-wrap: wrap;
    width: 100%;
  }

  .thumbnail-item {
    flex-shrink: 0;
  }

  .main-image-section,
  .info-section {
    max-width: 100%;
  }
}

/* ============ 下单确认弹窗样式 ============ */
:deep(.checkout-dialog) {
  border-radius: 12px;
  overflow: hidden;
  .el-dialog__header {
    background: #f5f7fa;
    margin: 0;
    padding: 16px 20px;
    border-bottom: 1px solid #ebeef5;
    .el-dialog__title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }
  .el-dialog__body {
    padding: 0;
  }
  .el-dialog__footer {
    padding: 0;
    border-top: 1px solid #ebeef5;
  }
}

.checkout-content {
  padding: 20px;
  background: #fdfdfd;
}

.checkout-goods-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 20px;

  .goods-cover {
    width: 60px;
    height: 60px;
    border-radius: 4px;
    flex-shrink: 0;
    background: #f5f7fa;
  }

  .goods-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;

    .goods-title {
      font-size: 14px;
      color: #303133;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .goods-price-row {
      text-align: right;
      .price {
        font-size: 16px;
        font-weight: 600;
        color: #f56c6c;
      }
    }
  }
}

.checkout-section {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;

  &:last-child {
    margin-bottom: 0;
  }

  .section-header {
    margin-bottom: 12px;
    .title {
      font-size: 15px;
      font-weight: 600;
      color: #303133;
    }
  }
}

.address-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 200px;
  overflow-y: auto;

  /* 隐藏滚动条但保留功能 */
  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: #dcdfe6;
    border-radius: 3px;
  }
}

.address-item {
  position: relative;
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #c0c4cc;
    background: #fcfcfc;
  }

  &.is-selected {
    border-color: #409EFF;
    background: #ecf5ff;
  }

  .address-main {
    flex: 1;
    .contact-info {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
      .name {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
      }
      .phone {
        font-size: 13px;
        color: #606266;
      }
    }
    .address-detail {
      font-size: 12px;
      color: #909399;
      line-height: 1.4;
    }
  }

  .check-icon {
    font-size: 20px;
    color: #409EFF;
    margin-left: 12px;
  }
}

.empty-address {
  text-align: center;
  padding: 10px 0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;

  .label {
    color: #606266;
  }

  .value {
    color: #303133;
    font-weight: 500;
  }

  .pay-method {
    display: flex;
    align-items: center;
    gap: 6px;
  }
}

.checkout-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fff;

  .total-price {
    font-size: 14px;
    color: #606266;
    .price {
      font-size: 20px;
      font-weight: 600;
      color: #f56c6c;
    }
  }

  .actions {
    display: flex;
    gap: 12px;
  }
}
</style>
