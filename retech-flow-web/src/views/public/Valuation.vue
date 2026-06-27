<template>
  <div class="valuation-page">
    <div class="page-header">
      <h1 class="page-title">
        <span class="gradient-text">AI</span> 智能估价
      </h1>
      <p class="page-sub">上传实拍图和设备描述，自动识别型号、成色并生成参考价格</p>
    </div>

    <el-row :gutter="32" class="main-layout">
      <!-- 左侧：输入区 -->
      <el-col :span="12" class="left-col">
        <div class="input-panel">

          <!-- Step 1: 上传图片 -->
          <div class="step-block upload-block">
            <div class="step-label">
              <span class="label-text">上传设备图片</span>
              <span class="step-tip">
                最多4张，建议拍摄正面、背面、屏幕、瑕疵处
                <el-popover
                  placement="top-start"
                  title="图片上传说明"
                  :width="220"
                  trigger="hover"
                  content="请上传清晰的实景图片，建议包含设备的设备详情页、正面、背面、侧面、屏幕及任何瑕疵处，以便 AI 精准评估成色。"
                >
                  <template #reference>
                    <el-icon class="tips-icon"><QuestionFilled /></el-icon>
                  </template>
                </el-popover>
              </span>
            </div>
            <el-upload
              v-model:file-list="fileList"
              action="#"
              list-type="picture-card"
              :auto-upload="false"
              :limit="4"
              :on-exceed="handleExceed"
              class="image-uploader"
              :class="{ 'hide-trigger': fileList.length >= 4 }"
            >
              <template #default>
                <div class="upload-placeholder">
                  <div class="upload-icon-wrapper">
                    <el-icon :size="28"><Camera /></el-icon>
                    <div class="scan-line"></div>
                  </div>
                  <span>点击上传</span>
                </div>
              </template>
              <template #file="{ file }">
                <div class="upload-item">
                  <img :src="file.url" class="upload-img" />
                  <div class="upload-actions">
                    <el-icon @click="handleRemove(file)"><Delete /></el-icon>
                  </div>
                </div>
              </template>
            </el-upload>
          </div>

          <!-- Step 2: 文字描述 -->
          <div class="step-block desc-block">
            <div class="step-label">
              <span class="label-text">描述设备状况</span>
              <span class="step-tip">AI 将根据您的描述精准定价</span>
            </div>

            <div class="desc-input-wrapper">
              <el-input
                v-model="form.description"
                type="textarea"
                placeholder="请输入设备详细情况...
例如：
- 屏幕是否有划痕？
- 电池健康度是多少？
- 是否有拆修记录？
- 配件是否齐全？"
                maxlength="500"
                show-word-limit
                resize="none"
                class="desc-input"
              />
              <div class="input-corner-decoration top-left"></div>
              <div class="input-corner-decoration top-right"></div>
              <div class="input-corner-decoration bottom-left"></div>
              <div class="input-corner-decoration bottom-right"></div>
            </div>

            <div class="quick-tags">
              <span class="tags-label">快速特征：</span>
              <div class="tags-list">
                <el-check-tag
                  v-for="tag in quickTags"
                  :key="tag"
                  :checked="selectedTags.includes(tag)"
                  @change="toggleTag(tag)"
                  class="quick-tag"
                >
                  {{ tag }}
                </el-check-tag>
              </div>
            </div>
          </div>

          <!-- 提交按钮 -->
          <div class="submit-wrapper">
            <button
              class="ai-submit-btn"
              :class="{ 'is-analyzing': valuationStore.isValuating }"
              :disabled="!canSubmit || valuationStore.isValuating"
              @click="handleAnalyze"
            >
              <div class="btn-content">
                <el-icon v-if="!valuationStore.isValuating" class="btn-icon"><MagicStick /></el-icon>
                <span class="btn-text">{{ valuationStore.isValuating ? 'AI 正在深度估算...' : '开始 AI 估价' }}</span>
              </div>
              <div v-if="valuationStore.isValuating" class="loading-wave">
                <span></span><span></span><span></span><span></span><span></span>
              </div>
              <div class="btn-glow"></div>
            </button>
          </div>

        </div>
      </el-col>

      <!-- 右侧：结果区 -->
      <el-col :span="12" class="right-col">
        <div class="result-panel">

          <!-- 估价失败状态 -->
          <div v-if="valuationStore.valuationError && !valuationStore.isValuating" class="result-empty result-error">
            <div class="error-content">
              <div class="error-heading">
                <div class="error-icon">
                  <el-icon><WarningFilled /></el-icon>
                </div>
                <div>
                  <span>识别未通过</span>
                  <h3>本次估价未完成</h3>
                </div>
              </div>

              <div class="error-reason">
                <span>系统反馈</span>
                <p>{{ cleanValuationError }}</p>
              </div>

              <div class="error-checklist">
                <div><el-icon><CircleCheck /></el-icon><span>请上传真实的二手数码产品图片</span></div>
                <div><el-icon><CircleCheck /></el-icon><span>确保主体完整、清晰且光线充足</span></div>
                <div><el-icon><CircleCheck /></el-icon><span>避免人物、截图或与设备无关的内容</span></div>
              </div>

              <button class="error-retry-btn" type="button" @click="handleAnalyze">
                <el-icon><Refresh /></el-icon>
                <span>重新尝试</span>
              </button>
            </div>
          </div>

          <!-- 未估价状态 -->
          <div v-else-if="!hasResult && !valuationStore.isValuating" class="result-empty">
            <div class="empty-content">
              <div class="ai-scan-container">
                <div class="device-icon">
                  <el-icon :size="64"><Iphone /></el-icon>
                </div>
                <div class="scan-beam"></div>
                <div class="scan-grid"></div>
                <div class="ai-badge">AI Identifying</div>
              </div>

              <div class="empty-text">
                <h3>AI 智能鉴别 · 精准定价</h3>
                <p>上传图片自动识别成色，大数据实时比对</p>
                <div class="features-tags">
                  <span>🚀 秒级出价</span>
                  <span>💎 市场行情</span>
                  <span>📝 自动文案</span>
                </div>
              </div>
            </div>
          </div>

          <!-- AI 深度分析：深色神秘科技风等待动画 -->
          <div v-if="valuationStore.isValuating" class="ai-mystery-analysis">
            <!-- 取消估价按钮 -->
            <button
              class="cancel-valuation-btn"
              type="button"
              @click="cancelValuation"
            >
              <el-icon><Close /></el-icon>
              <span>取消</span>
            </button>

            <div class="mystery-bg-glow"></div>

            <div class="mystery-content">
              <!-- 图片展示与呼吸灯边框 -->
              <div class="mystery-image-container" v-if="firstUploadedImage">
                <div class="image-glow-border"></div>
                <img :src="firstUploadedImage" class="mystery-image" alt="user uploaded item" />

                <!-- 放大镜扫描动画 -->
                <div class="mystery-scanner">
                  <div class="scanner-glass"></div>
                </div>
              </div>

              <!-- Gemini AI 风格图标 -->
              <div class="mystery-ai-icon" v-else>
                <div class="gemini-star"></div>
                <div class="gemini-star small"></div>
              </div>

              <!-- 打字机消息展示 -->
              <div class="mystery-messages">
                <div
                  v-for="(msg, idx) in activeMessages"
                  :key="idx"
                  class="mystery-message-item"
                  :class="{ 'is-entering': true }"
                >
                  <span class="msg-dot"></span>
                  <span class="msg-text">{{ msg }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 估价结果 -->
          <div v-if="hasResult && !valuationStore.isValuating" class="result-content">

            <!-- 价格区间 -->
            <el-card class="result-card price-card" shadow="never">
              <div class="result-section-title">
                <span class="title-text">参考估价区间</span>
              </div>
              <div class="price-display">
                <div class="price-range-container">
                  <div class="price-range-main">
                    <span class="currency">¥</span>
                    <span class="amount">{{ result.priceMin }}</span>
                    <span class="separator">-</span>
                    <span class="amount">{{ result.priceMax }}</span>
                  </div>
                  <div class="price-badge">
                    <span class="label">建议发布价</span>
                    <span class="value">¥{{ result.suggestPrice }}</span>
                    <span class="price-badge-note">结合当前成色与行情</span>
                  </div>
                </div>
              </div>
            </el-card>

            <!-- 一键生成文案 -->
            <el-card class="result-card copy-card" shadow="never">
              <div class="result-section-title">
                <span class="title-text">AI 生成发布文案</span>
                <span class="regenerate-tip">结果不满意？</span>
                <button
                  class="regenerate-btn"
                  @click="handleRegenerate"
                  :disabled="isRegenerating"
                >
                  <el-icon :class="{ 'is-spinning': isRegenerating }"><Refresh /></el-icon>
                  <span>{{ isRegenerating ? '生成中' : '重新生成' }}</span>
                </button>
              </div>

              <div class="copy-content-wrapper">
                <div class="copy-block" :class="{ 'is-streaming': isTypingTitle }">
                  <div class="copy-label">标题</div>
                  <div class="input-glow-wrapper">
                    <el-input
                      v-model="displayedTitle"
                      placeholder="生成的标题"
                      class="title-input"
                      :disabled="valuationStore.isValuating || isRegenerating"
                    />
                    <div class="glow-border"></div>
                  </div>
                </div>
                <div class="copy-block" :class="{ 'is-streaming': isTypingDesc }">
                  <div class="copy-label">详情文案</div>
                  <div class="input-glow-wrapper textarea-glow-wrapper">
                    <el-input
                      v-model="displayedDesc"
                      type="textarea"
                      placeholder="生成的详情文案"
                      resize="none"
                      maxlength="500"
                      show-word-limit
                      :autosize="{ minRows: 5, maxRows: 16 }"
                      class="desc-input-area"
                      :disabled="valuationStore.isValuating || isRegenerating"
                    />
                    <div class="glow-border"></div>
                  </div>
                </div>
              </div>

              <el-row :gutter="12" class="action-buttons">
                <el-col :span="12">
                  <el-button style="width:100%" @click="handleCopy" size="default">
                    <el-icon><CopyDocument /></el-icon>
                    复制文案
                  </el-button>
                </el-col>
                <el-col :span="12">
                  <el-button type="primary" style="width:100%" @click="handlePublish" size="default">
                    <el-icon><Promotion /></el-icon>
                    一键发布
                  </el-button>
                </el-col>
              </el-row>
            </el-card>

          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: 'Valuation'
})

import {
  Camera,
  Delete,
  MagicStick,
  CopyDocument,
  Promotion,
  Refresh,
  Iphone,
  QuestionFilled,
  WarningFilled,
  Close,
  CircleCheck
} from '@element-plus/icons-vue'
import { ref, computed, onUnmounted, onActivated, onDeactivated, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import goodsApi from '@/api/goodsapi'
import { useRouter } from 'vue-router'
import { useValuationStore } from '@/store/valuationStore'
import { useTypewriter } from '@/composables/useTypewriter'
import { useUserStore } from '@/store/userstore'
import { openAuthDialog } from '@/composables/useAuthDialog'
import { hasUsedGuestValuation, markGuestValuationUsed } from '@/utils/guestSession'

const router = useRouter()
const valuationStore = useValuationStore()
const userStore = useUserStore()
const { isTypingTitle, isTypingDesc, start: startTyping} = useTypewriter()

// ---- 页面激活/失活 ----
onActivated(() => {
  valuationStore.isOnPage = true
})

onDeactivated(() => {
  valuationStore.isOnPage = false
})

// ---- 表单数据 ----
const form = ref({
  description: '',
})
const fileList = ref<any[]>([])
const uploadedTempPaths = ref<string[]>([])
const selectedTags = ref<string[]>([])
const quickTags = ['无拆修', '原包装', '电池健康90%+', '无划痕', '屏幕完好', '国行', '在保', '贴膜使用', '配件齐全']

const toggleTag = (tag: string) => {
  const idx = selectedTags.value.indexOf(tag)
  if (idx > -1) {
    selectedTags.value.splice(idx, 1)
    form.value.description = form.value.description.replace(`${tag}、`, '').replace(tag, '')
  } else {
    selectedTags.value.push(tag)
    form.value.description += (form.value.description ? '、' : '') + tag
  }
}

const handleExceed = () => {
  ElMessage.warning('最多上传4张图片')
}

const handleRemove = (file: any) => {
  const idx = fileList.value.findIndex(f => f.uid === file.uid)
  if (idx > -1) fileList.value.splice(idx, 1)
}

const canSubmit = computed(() =>
  form.value.description || fileList.value.length > 0
)

const isRegenerating = ref(false)
const cleanValuationError = computed(() =>
  (valuationStore.valuationError || '请稍后重试').replace(/^安检未通过[：:]/, '')
)

// 本地结果展示（从 store 同步）
const hasResult = ref(false)
const result = ref({
  priceMin: 0,
  priceMax: 0,
  suggestPrice: 0,
  generatedTitle: '',
  generatedDesc: '',
})

// 获取用户上传的第一张图片用于展示
const firstUploadedImage = computed(() => {
  if (fileList.value.length > 0 && fileList.value[0].url) {
    return fileList.value[0].url
  }
  return null
})

// 打字机效果（复用 composable）
const displayedTitle = ref('')
const displayedDesc = ref('')

/** AI 深度分析分步动画 */
const analysisStepDefs = [
  '分析照片中的宝贝...',
  '鉴定宝贝的成色外观磨损等...',
  '搜集全网宝贝相关价格...',
  '计算二手折旧评估价格...',
  '热卖标题文案创作中...',
  '即将完成智能估价鉴定...'
]

const activeMessages = ref<string[]>([])
let messageTimer: any = null

function startMysteryAnimation() {
  activeMessages.value = []
  let step = 0
  const stepDuration = 5000

  const showNextMessage = () => {
    if (!valuationStore.isValuating || step >= analysisStepDefs.length) return
    const msg = analysisStepDefs[step]
    if (msg) {
      activeMessages.value.push(msg)
    }
    if (activeMessages.value.length > 3) {
      activeMessages.value.shift()
    }
    step++
    if (step < analysisStepDefs.length) {
      messageTimer = setTimeout(showNextMessage, stepDuration)
    }
  }
  showNextMessage()
}

function stopMysteryAnimation() {
  if (messageTimer) {
    clearTimeout(messageTimer)
    messageTimer = null
  }
}

// ---- 监听 store 中的估价结果 ----
watch(
  () => valuationStore.valuationResult,
  (newResult) => {
    if (!newResult) return

    stopMysteryAnimation()

    result.value = {
      priceMin: newResult.min_price,
      priceMax: newResult.max_price,
      suggestPrice: Math.floor((newResult.min_price + newResult.max_price) / 2),
      generatedTitle: newResult.title || '',
      generatedDesc: newResult.description || '',
    }
    hasResult.value = true

    // 如果在估价页面，执行打字机效果
    if (valuationStore.isOnPage) {
      startTyping(
        result.value.generatedTitle, displayedTitle,
        result.value.generatedDesc, displayedDesc
      )
    } else {
      // 不在页面，直接填充
      displayedTitle.value = result.value.generatedTitle
      displayedDesc.value = result.value.generatedDesc
    }

    // 重新生成完成
    if (isRegenerating.value) {
      isRegenerating.value = false
    }
  }
)

// 监听估价错误
watch(
  () => valuationStore.valuationError,
  (err) => {
    if (!err) return
    stopMysteryAnimation()

    if (isRegenerating.value) {
      isRegenerating.value = false
    }

    if (valuationStore.isOnPage) {
      const cleanMsg = err.replace(/^安检未通过[：:]/, '')
      ElMessage.error(cleanMsg)
    }
  }
)

// ---- 取消估价（障眼法） ----
const cancelValuation = () => {
  valuationStore.cancelTask()
  stopMysteryAnimation()
  isRegenerating.value = false
  ElMessage.info('已取消估价')
}

// ---- 提交估价 ----
const handleAnalyze = async () => {
  if (!canSubmit.value) return

  if (!userStore.isLoggedIn && hasUsedGuestValuation()) {
    ElMessage.info('游客仅可体验一次估价，登录后可继续使用')
    openAuthDialog('login')
    return
  }

  if (fileList.value.length === 0) {
    ElMessage.warning('请至少上传一张商品图片！')
    return
  }

  hasResult.value = false
  displayedTitle.value = ''
  displayedDesc.value = ''
  valuationStore.clearResults()

  try {
    // 先上传图片
    uploadedTempPaths.value = []
    for (const file of fileList.value) {
      if (file.raw) {
        const formData = new FormData()
        formData.append('image', file.raw)
        const uploadRes = await goodsApi.uploadImageAPI(formData)
        if (uploadRes.code === 200) {
          uploadedTempPaths.value.push(uploadRes.data.file_path)
        } else {
          throw new Error('图片上传失败：' + uploadRes.msg)
        }
      }
    }

    // 发送异步估价请求
    const payload = {
      user_desc: form.value.description,
      image_paths: uploadedTempPaths.value
    }

    const res = await goodsApi.valuationAPI(payload)

    if (res.code === 200 && res.data?.task_id) {
      if (!userStore.isLoggedIn) markGuestValuationUsed()
      // 拿到 task_id，存入 store，启动 loading 和动画
      valuationStore.startTask(res.data.task_id)
      startMysteryAnimation()
    } else {
      ElMessage.error(res.msg || '提交估价失败')
    }
  } catch (error: any) {
    console.error('估价提交出错:', error)
    if (!userStore.isLoggedIn && error.response?.status === 403) {
      markGuestValuationUsed()
      openAuthDialog('login')
      return
    }
    ElMessageBox.alert(
      error.response?.data?.msg || error.message || '网络请求失败，请检查网络或稍后重试',
      '啊哦',
      { confirmButtonText: '知道了', type: 'error', center: true }
    )
  }
}

// ---- 重新生成 ----
const handleRegenerate = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.info('登录后可再次估价并重新生成文案')
    openAuthDialog('login')
    return
  }

  if (fileList.value.length === 0) {
    ElMessage.warning('请至少上传一张商品图片！')
    return
  }

  isRegenerating.value = true
  displayedTitle.value = ''
  displayedDesc.value = ''
  hasResult.value = false

  startMysteryAnimation()

  try {
    const payload = {
      user_desc: form.value.description,
      image_paths: uploadedTempPaths.value
    }

    const res = await goodsApi.valuationAPI(payload)

    if (res.code === 200 && res.data?.task_id) {
      valuationStore.startTask(res.data.task_id)
    } else {
      stopMysteryAnimation()
      isRegenerating.value = false
      ElMessage.error(res.msg || '重新生成失败')
    }
  } catch (error: any) {
    console.error('重新生成请求出错:', error)
    stopMysteryAnimation()
    isRegenerating.value = false
    ElMessageBox.alert(
      error.response?.data?.msg || error.message || '网络请求失败',
      '啊哦',
      { confirmButtonText: '知道了', type: 'error', center: true }
    )
  }
}

const handleCopy = () => {
  const text = `${displayedTitle.value}\n\n${displayedDesc.value}`
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('文案已复制到剪贴板')
  })
}

const handlePublish = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.info('登录后可一键发布商品')
    openAuthDialog('login')
    return
  }

  if (!result.value.generatedTitle || !result.value.generatedDesc) {
    ElMessage.warning('请等待 AI 生成文案后再发布')
    return
  }

  const draftData = {
    title: displayedTitle.value,
    description: displayedDesc.value,
    price: result.value.suggestPrice,
    category_id: undefined,
    delivery_method: 1,
    image_urls: uploadedTempPaths.value,
    attributes: {}
  }

  localStorage.setItem('publish_draft', JSON.stringify(draftData))

  ElMessage.success('已生成草稿，正在跳转至发布页面...')
  router.push({ path: '/orders/publish', query: { auto_load: '1' } })
}

onUnmounted(() => {
  stopMysteryAnimation()
  valuationStore.isOnPage = false
})
</script>

<style scoped lang="scss" src="../../styles/Valuation.scss"></style>
