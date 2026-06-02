<template>
  <div class="wf-card" @click="onClick">
    <!-- 封面图 -->
    <div class="wf-img-wrap">
      <el-image
        :src="displayImage"
        fit="cover"
        lazy
        class="wf-img"
      >
        <template #placeholder>
          <div class="img-placeholder">
            <el-icon class="is-loading"><Loading /></el-icon>
          </div>
        </template>
        <template #error>
          <div class="img-error">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-image>

      <!-- 状态徽章 (如果有) -->
      <div v-if="statusText && showStatus" :class="['wf-status', getStatusClass(status)]">
        {{ statusText }}
      </div>

      <!-- 点赞徽章 (如果有) -->
      <div v-if="item.is_like" class="wf-like-badge">
        <el-icon color="#f56c6c"><svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M512 896a32 32 0 0 1-22.656-9.344l-339.2-339.2c-73.664-73.664-73.664-192.512 0-266.176s192.512-73.664 266.176 0L512 376.832l95.68-95.552c73.664-73.664 192.512-73.664 266.176 0s73.664 192.512 0 266.176l-339.2 339.2A32 32 0 0 1 512 896z"></path></svg></el-icon>
      </div>
    </div>

    <!-- 信息 -->
    <div class="wf-body">
      <h3 class="wf-title" :title="item.title">{{ item.title }}</h3>
      <div class="wf-price-row">
        <span class="wf-price">¥{{ formatPrice(item.price) }}</span>
        
        <!-- 元数据区域 (按需展示) -->
        <span v-if="metaType === 'views'" class="wf-meta">
          <el-icon><View /></el-icon> {{ item.views || 0 }}
        </span>
        <span v-else-if="metaType === 'wants'" class="wf-meta">
          <el-icon><Star /></el-icon> {{ item.wants || 0 }}人想要
        </span>
        
        <slot name="extra"></slot>
      </div>
      
      <!-- 卖家信息区域 -->
      <div class="wf-seller-row" v-if="item.seller">
        <el-avatar :size="24" :src="sellerAvatar" class="seller-avatar" />
        <span class="seller-name">{{ formatSellerName(item.seller.nickname || item.seller.username) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Picture, Loading, View, Star } from '@element-plus/icons-vue'
import { formatPrice, getImageUrl } from '@/utils/format'

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  // 是否显示状态徽章
  showStatus: {
    type: Boolean,
    default: false
  },
  // 底部右侧的描述文本，比如浏览量或收藏人数
  metaType: {
    type: String,
    default: 'views' // 'views', 'wants', 'none', custom text etc.
  }
})

const router = useRouter()

const sellerAvatar = computed(() => {
  const avatar = props.item.seller?.avatar
  return avatar ? getImageUrl(avatar) : ''
})

// 格式化卖家名称 (我是大美丽 -> 我是***丽)
const formatSellerName = (name: string | undefined) => {
  if (!name) return '神秘用户'
  if (name.length <= 2) {
    return name.substring(0, 1) + '*'
  }
  // 保留前2位和最后1位，中间全部替换为***
  return name.substring(0, 2) + '***' + name.substring(name.length - 1)
}

// 提取和处理图片
const displayImage = computed(() => {
  const i = props.item
  let imgPath = ""
  if (typeof i.cover === "string") imgPath = i.cover
  else if (i.cover?.image) imgPath = i.cover.image
  else if (i.image) imgPath = i.image
  else if (i.images && i.images.length > 0) {
    imgPath = typeof i.images[0] === "string" ? i.images[0] : i.images[0].image
  }
  return getImageUrl(imgPath)
})


// 状态处理
const statusText = computed(() => {
  if (props.item.statusText) return props.item.statusText
  const statusMap: Record<number, string> = {
    0: '草稿',
    1: '在售',
    2: '已下架',
    3: '已售出',
  }
  return statusMap[props.item.status] || ''
})

const status = computed(() => props.item.status)

function getStatusClass(statusVal: number) {
  const map: Record<number, string> = {
    0: 'draft',
    1: 'on_sale',
    2: 'offline',
    3: 'sold',
  }
  return `wf-status--${map[statusVal] || 'offline'}`
}

const onClick = () => {
  if (props.item.id) {
    const route = router.resolve(`/goods/${props.item.id}`)
    window.open(route.href, '_blank')
  }
}
</script>

<style scoped>
.wf-card {
  break-inside: avoid;
  margin-bottom: 0;
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  display: flex;
  flex-direction: column;
}

.wf-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
  border-color: #d0d0d0;
}

.wf-img-wrap {
  position: relative;
  background: #f5f5f5;
  width: 100%;
  aspect-ratio: 1 / 1;
  overflow: hidden;
}

.wf-img {
  width: 100%;
  height: 100%;
  display: block;
  transition: transform 0.5s ease;
}

.wf-card:hover .wf-img {
  transform: scale(1.03);
}

.img-placeholder,
.img-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  font-size: 24px;
}

/* 点赞徽章 */
.wf-like-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.9); /* 纯净的白色半透明背景 */
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  font-size: 18px;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  z-index: 2;
}

.wf-card:hover .wf-like-badge {
  transform: scale(1.15) rotate(10deg);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 状态徽章 */
.wf-status {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 10px;
  border-radius: 6px; /* 统一、温和的微小圆角 */
  font-size: 12px;
  font-weight: 500; /* 去掉粗体，改为中等字重，更精致 */
  color: #333333; /* 深灰色文字 */
  background: rgba(255, 255, 255, 0.85); /* 半透明纯白底色 */
  backdrop-filter: blur(4px); /* 保留你原本的毛玻璃，但减弱一点 */
  border: 1px solid rgba(0, 0, 0, 0.04); /* 极细的描边增加边缘清晰度 */
  z-index: 2;
}

.wf-card:hover .wf-status {
  transform: scale(1.05) translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.wf-status--on_sale {
  color: #fff;
  background: linear-gradient(135deg, #ff9a44 0%, #fc6076 100%);
  border: none;
}

.wf-status--sold {
  color: #fff;
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  border: none;
}

.wf-status--offline {
  color: #fff;
  background: linear-gradient(135deg, #8baaaa 0%, #ae8b9c 100%);
  border: none;
}

.wf-status--draft {
  color: #fff;
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
  border: none;
}

/* 卡片内容 */
.wf-body {
  padding: 14px 16px 16px;
  flex: 1; /* 让 body 撑满剩余空间，保证高度一致时内容对齐 */
  display: flex;
  flex-direction: column;
}

.wf-title {
  margin: 0 0 10px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4; /* 调整行高 */
  height: 2.8em; /* 固定两行高度: 1.4 * 2 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-all; /* 确保长单词也能换行 */
}

.wf-price-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
  margin-top: auto; /* 将价格行推到底部 */
}

.wf-price {
  font-size: 20px;
  font-weight: 700;
  color: #f56c6c;
  font-family: 'DIN Alternate', 'Helvetica Neue', sans-serif;
}

.wf-meta {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.wf-seller-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
}

.seller-avatar {
  flex-shrink: 0;
  border: 1px solid #f0f0f0;
}

.seller-name {
  font-size: 13px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
