<template>
  <DecorativeBackground>
  <div class="publish-page">
    <!-- ====== 顶部标题栏 ====== -->
    <div class="publish-topbar">
      <div class="topbar-left">
        <div class="topbar-icon">
          <el-icon :size="18"><Edit /></el-icon>
        </div>
        <h1 class="topbar-title">发布商品</h1>
        <span class="topbar-hint">详细的描述和清晰的图片能让商品更快售出</span>
      </div>
      <div class="topbar-actions">
        <el-button class="act-btn act-publish" @click="submitForm(formRef)" :loading="isPublishing">
          <el-icon><Upload /></el-icon>
          <span>发布</span>
        </el-button>
        <el-button class="act-btn act-draft" @click="saveDraft">
          <el-icon><DocumentCopy /></el-icon>
          <span>草稿</span>
        </el-button>
        <el-button class="act-btn act-draft-box" @click="showDraftBox = true">
          <el-icon><Box /></el-icon>
          <span>草稿箱</span>
        </el-button>
        <el-button class="act-btn act-clear" @click="clearDraft">
          <el-icon><Delete /></el-icon>
          <span>清空</span>
        </el-button>
      </div>
    </div>

    <!-- ====== 草稿箱弹窗 ====== -->
    <el-dialog
      v-model="showDraftBox"
      width="600px"
      append-to-body
      class="draft-box-dialog"
    >
      <template #header>
        <div class="draft-dialog-header">
          <span class="header-title">草稿箱</span>
          <span class="header-count" v-if="drafts.length > 0">({{ drafts.length }})</span>
        </div>
      </template>
      <div v-loading="loadingDrafts" class="draft-list">
        <div v-if="drafts.length === 0" class="draft-empty">
          <el-empty description="暂无草稿" :image-size="100" />
        </div>
        <div v-else v-for="item in drafts" :key="item.id" class="draft-item" @click="useDraft(item)">
          <div class="draft-cover">
            <el-image :src="getImageUrl(item.cover)" fit="cover">
              <template #error>
                <div class="image-slot"><el-icon><Picture /></el-icon></div>
              </template>
            </el-image>
          </div>
          <div class="draft-info">
            <div class="draft-title">{{ item.title || '无标题' }}</div>
            <div class="draft-desc">{{ item.description || '无描述' }}</div>
            <div class="draft-time">{{ formatTime(item.updated_at) || '未知时间' }}</div>
          </div>
          <div class="draft-actions" @click.stop>
            <el-button 
              type="danger" 
              link 
              :icon="Delete" 
              @click="handleDeleteDraft(item.id)"
            />
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- ====== 表单主体 ====== -->
    <el-form
      :model="form"
      :rules="rules"
      ref="formRef"
      label-position="top"
      class="publish-form"
      size="default"
    >
      <!-- ======== 双栏：图片 + 商品信息 ======== -->
      <div class="two-col-layout">
        <div class="col-left">
          <!-- 图片区 -->
          <div class="card">
            <div class="card-title">
              <span class="required-star">*</span>
              <span>商品图片</span>
              <span class="upload-limit-hint">最多9张，第一张为封面</span>
            </div>
            <el-form-item prop="image_urls" class="no-mb">
              <el-upload
                v-model:file-list="fileList"
                action="#"
                list-type="picture-card"
                :auto-upload="false"
                :limit="9"
                :on-change="handleImageChange"
                class="img-uploader"
                :class="{ 'hide-trigger': fileList.length >= 9 }"
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
                      <el-icon @click="handleRemoveFile(file)"><Delete /></el-icon>
                    </div>
                  </div>
                </template>
              </el-upload>
            </el-form-item>
          </div>

          <!-- 价格 + 分类 -->
          <div class="card">
            <div class="card-title">价格与分类</div>
            <el-form-item label="价格 (¥)" prop="price">
              <el-input-number
                v-model="form.price"
                :min="0.01"
                :precision="2"
                :step="10"
                controls-position="right"
                class="full-width"
              />
            </el-form-item>
            <el-form-item label="商品分类" prop="category_id" class="no-mb">
              <el-select
                v-model="form.category_id"
                placeholder="请选择分类"
                class="full-width"
                @change="handleCategoryChange"
              >
                <el-option
                  v-for="cat in categoryStore.categories"
                  :key="cat.id"
                  :label="cat.name"
                  :value="cat.id"
                />
              </el-select>
            </el-form-item>
          </div>

          <!-- 发货方式 -->
          <div class="card">
            <div class="card-title">发货方式</div>
            <el-form-item prop="delivery_method" class="no-mb">
              <div class="delivery-options">
                <div
                  v-for="method in categoryStore.shippingMethods"
                  :key="method.id"
                  class="delivery-chip"
                  :class="{ active: form.delivery_method === method.id }"
                  @click="form.delivery_method = method.id"
                >
                  {{ method.name }}
                </div>
              </div>
            </el-form-item>
          </div>
        </div>

        <div class="col-right">
          <div class="card">
            <div class="card-title card-title--actions">
              <span>商品信息</span>
              <div class="card-title-btns">
                <el-button v-if="hasBackup && !isAiAnalyzing" class="undo-btn" size="small" @click="undoAiAssist">
                  <el-icon><RefreshLeft /></el-icon>
                  撤销
                </el-button>
                <el-button class="ai-assist-btn" size="default" @click="triggerAiAssist" :disabled="isAiAnalyzing">
                  <el-icon><MagicStick /></el-icon>
                  {{ isAiAnalyzing ? '生成中...' : 'AI 帮我写' }}
                </el-button>
              </div>
            </div>

            <el-form-item label="商品标题" prop="title">
              <div class="input-glow-wrapper" :class="{ 'is-streaming': isAiAnalyzing || isTypingTitle }">
                <el-input
                  v-model="form.title"
                  placeholder="例如：99新苹果 iPhone 13 Pro Max"
                  maxlength="60"
                  show-word-limit
                />
                <div class="glow-border"></div>
              </div>
            </el-form-item>

            <el-form-item label="商品描述" prop="description">
              <div class="input-glow-wrapper textarea-glow-wrapper" :class="{ 'is-streaming': isAiAnalyzing || isTypingDesc }">
                <el-input
                  v-model="form.description"
                  type="textarea"
                  :rows="7"
                  placeholder="购买时间、使用情况、是否有划痕..."
                  maxlength="500"
                  show-word-limit
                  @input="handleDescriptionInput"
                />
                <div class="glow-border"></div>
              </div>
            </el-form-item>

            <!-- AI 分析进度面板 -->
            <transition name="ai-panel">
              <div v-if="isAiAnalyzing" class="ai-progress-panel">
                <div class="progress-inner">
                  <transition name="msg-switch" mode="out-in">
                    <div :key="currentMessage" class="progress-msg-item">
                      <span class="progress-diamond"></span>
                      <span class="progress-text">{{ currentMessage }}</span>
                    </div>
                  </transition>
                </div>
              </div>
            </transition>
          </div>

          <!-- 动态属性 -->
          <div class="card" v-if="currentCategoryAttributes.length > 0">
            <div class="card-title">商品属性</div>
            <div class="attr-list">
              <el-form-item
                v-for="attr in currentCategoryAttributes"
                :key="attr.name"
                :prop="`attributes.${attr.name}`"
                :rules="{ required: true, message: `请选择${attr.name}`, trigger: 'change' }"
                class="attr-row-item"
              >
                <div class="attr-row">
                  <span class="attr-label">{{ attr.name }}</span>
                  <div class="tag-options">
                    <div
                      v-for="opt in attr.options"
                      :key="opt"
                      class="tag-item"
                      :class="{ active: form.attributes[attr.name] === opt }"
                      @click="form.attributes[attr.name] = opt"
                    >
                      {{ opt }}
                    </div>
                  </div>
                </div>
              </el-form-item>
            </div>
          </div>
        </div>
      </div>
    </el-form>
  </div>
  </DecorativeBackground>
</template>

<script lang="ts" setup>
import { ref, reactive, toRef, onMounted, onUnmounted, onActivated, onDeactivated, computed, watch } from 'vue'
import { useRouter, useRoute, onBeforeRouteLeave } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules, UploadFile, UploadFiles } from 'element-plus'
import { Camera, MagicStick, RefreshLeft, Edit, Upload, DocumentCopy, Delete, Box, Picture } from '@element-plus/icons-vue'
import { useCategoryStore } from '@/store/categoryStore'
import { useTypewriter } from '@/composables/useTypewriter'
import { usePublishValuationStore } from '@/store/publishValuationStore'
import goodsApi from '@/api/goodsapi'
import DecorativeBackground from '@/components/DecorativeBackground.vue'
import { getImageUrl, formatTime } from '@/utils/format'

defineOptions({ name: 'Publish' })

const router = useRouter()
const route = useRoute()
const categoryStore = useCategoryStore()
const publishValuationStore = usePublishValuationStore()
const { isTypingTitle, isTypingDesc, start: startTyping, stop: stopTyping } = useTypewriter()
const formRef = ref<FormInstance>()

const isPublishing = ref(false)
const isAiAnalyzing = ref(false)

// 草稿箱相关
const showDraftBox = ref(false)
const drafts = ref<any[]>([])
const loadingDrafts = ref(false)

const fetchDrafts = async () => {
  loadingDrafts.value = true
  try {
    const res = await goodsApi.listMyPublishedAPI({ status: 0 })
    if (res.code === 200 && res.data) {
      // 兼容后端直接返回数组或对象包裹数组的情况
      drafts.value = Array.isArray(res.data) ? res.data : (res.data.list || [])
    } else {
      drafts.value = []
    }
  } catch (error) {
    console.error('获取草稿失败', error)
    ElMessage.error('草稿获取失败，请重试')
    drafts.value = []
  } finally {
    loadingDrafts.value = false
  }
}

watch(showDraftBox, (val) => {
  if (val) fetchDrafts()
})

const reuploadDraftImages = async (paths: string[]) => {
  const newPaths: string[] = []
  const newList: any[] = []
  
  for (let i = 0; i < paths.length; i++) {
    const path = paths[i]
    const url = getImageUrl(path)
    try {
      const response = await fetch(url)
      const blob = await response.blob()
      const file = new File([blob], `draft_image_${i}.jpg`, { type: blob.type || 'image/jpeg' })
      
      const formData = new FormData()
      formData.append('image', file)
      
      const res = await goodsApi.uploadImageAPI(formData)
      if (res.code === 200) {
        newPaths.push(res.data.file_path)
        newList.push({
          uid: Date.now() + i,
          name: file.name,
          url: getImageUrl(res.data.file_path),
          status: 'success',
          serverPath: res.data.file_path
        })
      }
    } catch (e) {
      console.error('重新上传草稿图片失败', e)
    }
  }
  return { newPaths, newList }
}

const useDraft = async (item: any) => {
  if (!item?.id) return
  
  try {
    const res = await goodsApi.getGoodsDetailAPI(item.id)
    if (res.code === 200 && res.data) {
      const detail = res.data
      form.title = detail.title || ''
      form.description = detail.description || ''
      form.price = detail.price || 0.00
      form.category_id = detail.category_id
      form.delivery_method = detail.delivery_method || 1
      form.attributes = detail.attributes || {}
      
      // 处理图片
      uploadedPaths.value = []
      fileList.value = []
      
      // 兼容后端返回的不同图片字段
      let images: string[] = []
      if (detail.images && Array.isArray(detail.images)) {
        // 后端详情接口通常返回 images 对象列表
        images = detail.images.map((img: any) => img.image)
      } else {
        images = detail.image_urls || detail.temp_images || []
      }
      
      if (images.length > 0) {
        const loadingMsg = ElMessage.info({ message: '正在提取并重新上传草稿图片，请稍候...', duration: 0 })
        const { newPaths, newList } = await reuploadDraftImages(images)
        uploadedPaths.value = newPaths
        form.image_urls = [...newPaths]
        fileList.value = newList as any
        loadingMsg.close()
      }
      showDraftBox.value = false
      
      // 草稿恢复成功后，直接从服务器端删除该草稿
      try {
        await goodsApi.deleteGoodsAPI(item.id)
        drafts.value = drafts.value.filter(d => d.id !== item.id)
      } catch (e) {
      }
      ElMessage.success('草稿恢复成功')
    }
  } catch (error) {
    console.error('获取草稿详情失败', error)
    ElMessage.error('草稿详情获取失败')
  }
}

const handleDeleteDraft = async (id: string) => {
  try {
    await ElMessageBox.confirm('确定要永久删除这份草稿吗？', '删除提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    
    const res = await goodsApi.deleteGoodsAPI(id)
    if (res.code === 200) {
      ElMessage.success('草稿已删除')
      fetchDrafts() // 刷新列表
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败', error)
      // 移除此处 redundant 的 ElMessage.error，拦截器已统一处理
    }
  }
}

const form = reactive({
  title: '',
  description: '',
  price: 0.00,
  category_id: undefined as number | undefined,
  delivery_method: 1,
  image_urls: [] as string[],
  attributes: {} as Record<string, string>
})

// 判断是否满足草稿保存条件：有图片、有标题 或 有描述 其中任意一个即可
// 且必须确保不是空草稿状态（比如只填了默认价格 0.00，其他全是空的就不提示）
const canSaveDraft = computed(() => {
  const hasTitle = form.title && form.title.trim() !== ''
  const hasDesc = form.description && form.description.trim() !== ''
  const hasImages = currentImagePaths.value.length > 0
  
  // 核心改动：只有这三个任意一个有真实内容，才认为是有效草稿，才会触发拦截提示
  return hasTitle || hasDesc || hasImages
})

// 动态获取当前选中分类的属性
const currentCategoryAttributes = computed(() => {
  if (!form.category_id) return []
  const cat = categoryStore.categories.find(c => c.id === form.category_id)
  return cat?.attributes || []
})

// 分类切换时清空已选属性
const handleCategoryChange = () => {
  form.attributes = {}
}

// Validation rules
const rules = reactive<FormRules>({
  title: [
    { required: true, message: '请输入商品标题', trigger: 'blur' },
    { min: 2, max: 60, message: '长度在 2 到 60 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入商品描述', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择商品分类', trigger: 'change' }
  ],
  delivery_method: [
    { required: true, message: '请选择发货方式', trigger: 'change' }
  ],
  image_urls: [
    { type: 'array', required: true, message: '请至少上传一张商品图片', trigger: 'change' }
  ]
})

// 图片上传处理
const fileList = ref<UploadFiles>([])

// 【核心】计算属性：实时获取当前所有已成功上传/恢复的图片路径
// 注意：Element Plus 的 UploadFile 在组件内部可能会丢失我们在 map 中附加的自定义属性（如 serverPath）
// 如果 file 对象有 response（通常是原生上传），我们取 response 中的数据
// 如果是手动构造的（如草稿恢复），则可能在 file.raw 或我们自己维护的列表中。
// 为了绝对可靠，我们恢复维护一个独立的图片路径数组。
const uploadedPaths = ref<string[]>([])

// 确保表单的校验和提交能拿到正确数据
const currentImagePaths = computed(() => {
  return uploadedPaths.value
})

const handleImageChange = async (file: UploadFile, files: UploadFiles) => {
  if (file.status === 'ready') {
    try {
      const formData = new FormData()
      formData.append('image', file.raw as Blob)
      const res = await goodsApi.uploadImageAPI(formData)
      if (res.code === 200) {
        uploadedPaths.value.push(res.data.file_path)
        form.image_urls = [...uploadedPaths.value] // 同步表单校验
        // 给 file 对象绑定一个 uid 到 path 的映射，方便删除
        ;(file as any).serverPath = res.data.file_path
        file.status = 'success'
      } else {
        ElMessage.error(res.msg || '上传失败')
        files.pop()
      }
    } catch (e) {
      ElMessage.error('图片上传异常')
      files.pop()
    }
  }
}

const handleRemoveFile = (file: UploadFile) => {
  // 无论是新上传的还是恢复的，都通过 serverPath 或者我们赋予的自定义属性来定位
  const path = (file as any).serverPath
  if (path) {
    const idx = uploadedPaths.value.indexOf(path)
    if (idx > -1) {
      uploadedPaths.value.splice(idx, 1)
      form.image_urls = [...uploadedPaths.value] // 同步表单校验
    }
  }
  const idx = fileList.value.findIndex((f: any) => f.uid === file.uid)
  if (idx > -1) {
    fileList.value.splice(idx, 1)
  }
}

// 关键词识别
const handleDescriptionInput = () => {
  // TODO: 后端目前未提供识别接口，前端本地字典已移除，保留事件以备后续接入。
}

// ===================== AI 帮我写（页内独立估价入口） =====================
const descriptionBackup = ref('')
const titleBackup = ref('')
const priceBackup = ref(0)
const hasBackup = ref(false)

// 分步分析消息（单条覆盖展示）
const analysisStepDefs = [
  '正在分析上传的图片...',
  '鉴定商品成色与外观...',
  '搜集全网同类商品价格...',
  '计算折旧与估价区间...',
  '智能生成标题与文案...',
  '即将完成，请稍候...'
]
const currentMessage = ref('')
let messageTimer: ReturnType<typeof setTimeout> | null = null

function startAnalysisAnimation() {
  currentMessage.value = ''
  let step = 0
  const stepDuration = 4000

  const showNext = () => {
    if (!isAiAnalyzing.value || step >= analysisStepDefs.length) return
    currentMessage.value = analysisStepDefs[step]!
    step++
    if (step < analysisStepDefs.length) {
      messageTimer = setTimeout(showNext, stepDuration)
    }
  }
  showNext()
}

function stopAnalysisAnimation() {
  if (messageTimer) {
    clearTimeout(messageTimer)
    messageTimer = null
  }
  currentMessage.value = ''
}

const triggerAiAssist = async () => {
  // 必须先上传图片，否则后端会拒绝
  if (currentImagePaths.value.length === 0) {
    ElMessage.warning('请先上传至少一张商品图片，AI才能分析哦')
    return
  }

  const tempDesc = form.description
  const tempTitle = form.title
  const tempPrice = form.price

  try {
    const payload = {
      user_desc: form.description || '帮我看看这个商品',
      image_paths: currentImagePaths.value
    }

    const res = await goodsApi.valuationAPI(payload)
    if (res.code === 200 && res.data?.task_id) {
      // 提交成功，显示进度
      isAiAnalyzing.value = true
      startAnalysisAnimation()
      
      // 保存备份
      descriptionBackup.value = tempDesc
      titleBackup.value = tempTitle
      priceBackup.value = tempPrice
      
      // 启动 WS 监听任务
      publishValuationStore.startTask(res.data.task_id)
      
      ElMessage.info('AI 正在分析中，请稍候...')
    } else {
      ElMessage.error(res.msg || 'AI 生成失败')
    }
  } catch (error) {
    console.error(error)
  }
}

// 监听 AI 估价成功结果
watch(
  () => publishValuationStore.valuationResult,
  (newVal) => {
    if (newVal && isAiAnalyzing.value) {
      stopAnalysisAnimation()
      isAiAnalyzing.value = false
      hasBackup.value = true
      
      // 模拟打字机效果填入数据
      const targetTitle = newVal.title || form.title
      const targetDesc = newVal.description || form.description
      form.price = Math.floor((newVal.min_price + newVal.max_price) / 2) || form.price
      
      form.title = ''
      form.description = ''
      
      startTyping(
        targetTitle,
        toRef(form, 'title') as any,
        targetDesc,
        toRef(form, 'description') as any
      ).then(() => {
        ElMessage.success('AI 帮我写完成')
        publishValuationStore.clearResults()
      })
    }
  }
)

// 监听 AI 估价失败
watch(
  () => publishValuationStore.valuationError,
  (err) => {
    if (err && isAiAnalyzing.value) {
      stopAnalysisAnimation()
      isAiAnalyzing.value = false
      // ElMessage.error(err) 会在 store 里抛出或自行处理
      publishValuationStore.clearResults()
    }
  }
)

const undoAiAssist = () => {
  form.description = descriptionBackup.value
  form.title = titleBackup.value
  form.price = priceBackup.value
  hasBackup.value = false
  ElMessage.success('已撤销 AI 的修改')
}

// ===================== 草稿功能 =====================
const DRAFT_KEY = 'publish_draft'

const saveDraft = async () => {
  // 仅在满足草稿保存条件时才执行保存逻辑
  if (!canSaveDraft.value) {
    ElMessage.info('暂无关键信息，未保存草稿')
    return
  }

  // 检查草稿箱数量，最多 10 个
  try {
    const checkRes = await goodsApi.listMyPublishedAPI({ status: 0 })
    if (checkRes.code === 200 && checkRes.data) {
      const currentDrafts = Array.isArray(checkRes.data) ? checkRes.data : (checkRes.data.list || [])
      if (currentDrafts.length >= 10) {
        ElMessage.warning('草稿箱已满，最多只能保存 10 个草稿，请先清理')
        showDraftBox.value = true 
        return
      }
    }
  } catch (error) {
  }

  try {
    const payload = {
      title: form.title || '',
      description: form.description || '',
      price: form.price || 0,
      category_id: form.category_id,
      delivery_method: form.delivery_method,
      temp_images: currentImagePaths.value,
      status: 0,
      attributes: form.attributes
    }
    const res = await goodsApi.saveDraftAPI(payload as any)
    if (res.code === 200) {
      localStorage.removeItem(DRAFT_KEY)
      ElMessage.success('草稿保存成功！')
      clearDraft(true) // 保存成功后清空当前表单
    } else {
      // 服务端保存失败，回退到本地存储
      localStorage.setItem(DRAFT_KEY, JSON.stringify({ ...form, image_urls: currentImagePaths.value }))
      ElMessage.warning(res.msg || '服务器保存失败，已保存到本地')
    }
  } catch (error) {
    localStorage.setItem(DRAFT_KEY, JSON.stringify({ ...form, image_urls: currentImagePaths.value }))
    ElMessage.warning('服务器保存失败，已保存到本地')
  }
}

const clearDraft = (silent = false) => {
  if (isAiAnalyzing.value) {
    stopAnalysisAnimation()
    isAiAnalyzing.value = false
  }
  localStorage.removeItem(DRAFT_KEY)
  form.title = ''
  form.description = ''
  form.price = 0.00
  form.category_id = undefined
  form.delivery_method = 1
  form.image_urls = []
  form.attributes = {}
  
  // 核心：清空真理源，才能真正让 canSaveDraft 计算为 false
  uploadedPaths.value = []
  fileList.value = []
  hasBackup.value = false
  
  if (!silent) ElMessage.success('草稿已清空')
}

const loadDraft = () => {
  const draftStr = localStorage.getItem(DRAFT_KEY)
  if (draftStr) {
    if (route.query.auto_load === '1') {
      try {
        const draft = JSON.parse(draftStr)
        Object.assign(form, draft)
        if (form.image_urls && form.image_urls.length > 0) {
          const images = [...form.image_urls]
          const loadingMsg = ElMessage.info({ message: '正在恢复本地草稿图片，请稍候...', duration: 0 })
          reuploadDraftImages(images).then(({ newPaths, newList }) => {
            uploadedPaths.value = newPaths
            form.image_urls = [...newPaths]
            fileList.value = newList as any
            loadingMsg.close()
          }).catch(() => loadingMsg.close())
        }
      } catch (e) {
        console.error('Failed to parse draft', e)
      }
      return
    }

    ElMessageBox.confirm(
      '检测到上次未完成的草稿内容，是否恢复？',
      '恢复草稿',
      {
        confirmButtonText: '恢复',
        cancelButtonText: '不用了',
        type: 'info',
      }
    ).then(() => {
      try {
        const draft = JSON.parse(draftStr)
        Object.assign(form, draft)
        if (form.image_urls && form.image_urls.length > 0) {
          const images = [...form.image_urls]
          const loadingMsg = ElMessage.info({ message: '正在恢复本地草稿图片，请稍候...', duration: 0 })
          reuploadDraftImages(images).then(({ newPaths, newList }) => {
            uploadedPaths.value = newPaths
            form.image_urls = [...newPaths]
            fileList.value = newList as any
            loadingMsg.close()
          }).catch(() => loadingMsg.close())
        }
        localStorage.removeItem(DRAFT_KEY) // 恢复后清除，避免重复提示
      } catch (e) {
        console.error('Failed to parse draft', e)
      }
    }).catch(() => {
      // 用户选择不恢复，清除本地草稿
      localStorage.removeItem(DRAFT_KEY)
    })
  }
}

onMounted(async () => {
  if (categoryStore.categories.length === 0) {
    await categoryStore.fetchCategories()
  }
  loadDraft()
  
  publishValuationStore.isOnPage = true
  publishValuationStore.connectWS()
})

// watch route query for auto_load when navigating to already-mounted Publish component (e.g. from Valuation in same keep-alive frame)
watch(
  () => route.query.auto_load,
  (newVal) => {
    if (newVal === '1') {
      loadDraft()
      // 清除 url 参数避免刷新再次自动加载
      const query = { ...route.query }
      delete query.auto_load
      router.replace({ query })
    }
  }
)

// keep-alive 激活/失活管理，从估价页一键发布跳转过来时，keep-alive 不会触发 onMounted，需在此加载草稿
onActivated(() => {
  if (route.query.auto_load === '1') {
    loadDraft()
    const query = { ...route.query }
    delete query.auto_load
    router.replace({ query })
  }
})

onDeactivated(() => {
})

// ===================== 路由守卫：离开页面提醒 =====================
const isSubmitting = ref(false) // 标记是否正在提交（发布或保存草稿），若是则不弹窗

// 判断表单是否有改动（用于决定是否提示离开）
const isFormDirty = computed(() => {
  return canSaveDraft.value
})

onBeforeRouteLeave(async () => {
  // 如果正在主动提交（发布或主动保存），直接放行
  if (isSubmitting.value || isPublishing.value) return true

  // 如果表单没有任何关键数据，直接清空数据并离开
  if (!isFormDirty.value) {
    clearDraft(true)
    return true
  }

  try {
    const action = await ElMessageBox.confirm(
      '您的商品信息尚未发布，是否保存为草稿？',
      '离开提醒',
      {
        confirmButtonText: '保存草稿',
        cancelButtonText: '直接离开',
        distinguishCancelAndClose: true,
        type: 'warning',
      }
    )
    if (action === 'confirm') {
      await saveDraft()
      return true
    }
  } catch (error) {
    if (error === 'cancel') {
      // 用户点击“直接离开”
      clearDraft(true) // 显式调用清空数据，确保不会被 keep-alive 缓存
      return true
    }
    // 关闭弹窗（点击遮罩或 ESC），不离开
    return false
  }
})

onUnmounted(() => {
  stopAnalysisAnimation()
  stopTyping()
  publishValuationStore.isOnPage = false
  publishValuationStore.reset()
})

// ===================== 发布提交 =====================
const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return

  await formEl.validate(async (valid, fields) => {
    if (valid) {
      isPublishing.value = true
      isSubmitting.value = true // 标记正在主动提交（发布），拦截 onBeforeRouteLeave 提示
      try {
        const payload = {
          title: form.title,
          description: form.description,
          price: form.price,
          category_id: form.category_id!,
          delivery_method: form.delivery_method,
          temp_images: currentImagePaths.value,
          status: 1,
          attributes: form.attributes
        }

        const res = await goodsApi.createGoodsAPI(payload)
        if (res.code === 200) {
          ElMessage.success('商品发布成功！')
          clearDraft(true) // 清空表单、Pinia 状态、localStorage
          router.push('/orders/published')
        } else {
          console.error("发布失败，接口返回:", res)
          isSubmitting.value = false // 失败后解除拦截
        }
      } catch (error) {
        console.error(error)
        isSubmitting.value = false // 失败后解除拦截
      } finally {
        isPublishing.value = false
      }
    } else {
      console.log('表单校验失败', fields)
    }
  })
}
</script>

<style scoped lang="scss" src="../../styles/Publish.scss"></style>
