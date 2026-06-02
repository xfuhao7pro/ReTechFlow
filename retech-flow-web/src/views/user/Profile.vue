<template>
  <div class="profile-page">

    <div class="profile-container" v-loading="loading">
      
      <!-- 1. 顶部渐变背景区 -->
      <div class="profile-header-bg">
      </div>

      <!-- 3. 下半部分白色区域 -->
      <div class="profile-content-area">
        <!-- 背景装饰元素 - 仅填充白色区域 -->
        <div class="decorative-bg-wrapper decorative-bg">
          <div class="ink-splash-1"></div>
          <div class="ink-splash-2"></div>
          <div class="line-decoration-1"></div>
          <div class="line-decoration-2"></div>
          <div class="line-decoration-3"></div>
          <div class="line-decoration-4"></div>
          <div class="curve-line-1"></div>
          <div class="curve-line-2"></div>
          <div class="dot-pattern-1"></div>
          <div class="dot-pattern-2"></div>
        </div>
        
        <div class="profile-layout-inner">
          <div class="banner-right">
            <el-button 
              type="primary" 
              plain
              class="edit-profile-btn"
              @click="toggleEditMode"
            >
              <el-icon class="el-icon--left"><Edit /></el-icon>
              {{ isEditing ? '取消编辑' : '编辑信息' }}
            </el-button>
          </div>
          
          <div class="profile-user-header">
            <div class="avatar-wrapper">
              <el-upload
                class="avatar-uploader"
                action="/users/avatar/upload/" 
                :show-file-list="false"
                :before-upload="beforeAvatarUpload"
                :http-request="handleAvatarUpload"
              >
                <el-avatar 
                  v-if="formData.avatar" 
                  :size="100" 
                  :src="getFullAvatarUrl" 
                  class="avatar-preview"
                />
                <div v-else class="avatar-placeholder">
                  <el-icon class="avatar-uploader-icon"><Plus /></el-icon>
                </div>
                <div class="avatar-hover-mask">
                  <el-icon><Camera /></el-icon>
                  <span>更换头像</span>
                </div>
              </el-upload>
            </div>
            
            <div class="user-summary-info">
              <div class="name-row">
                <h2 class="user-nickname">{{ formData.nickname || '未设置全名' }}</h2>
                <el-tag 
                  v-if="formData.is_verified" 
                  type="success" 
                  effect="light" 
                  round
                  size="small"
                  class="verified-tag"
                >
                  <div class="tag-content">
                    <el-icon><Select /></el-icon> 已实名认证
                  </div>
                </el-tag>
                <el-tag 
                  v-else 
                  type="info" 
                  effect="light" 
                  round
                  size="small"
                  class="verified-tag"
                >
                  <div class="tag-content">
                    <el-icon><Warning /></el-icon> 未实名认证
                  </div>
                </el-tag>
              </div>
              <div class="time-row">
                <span class="join-time">
                  <el-icon><Calendar /></el-icon> 注册于 {{ formatTime(formData.date_joined).split(' ')[0] }}
                </span>
              </div>
            </div>
          </div>

          <div class="info-card">
            <div class="card-header">
              <span class="card-title">个人信息</span>
            </div>

            <div class="card-body">
              <!-- 纯展示模式 (无边框) -->
              <div v-if="!isEditing" class="info-readonly-grid">
              <div class="info-item">
                <span class="info-label"><el-icon><Message /></el-icon> 电子邮件</span>
                <span class="info-value">
                  <span class="value-text">{{ formData.email || '未绑定' }}</span>
                  <el-tag v-if="formData.email" type="success" class="inline-tag">已绑定</el-tag>
                </span>
              </div>
              <div class="info-item">
                <span class="info-label"><el-icon><Location /></el-icon> 地址</span>
                <span class="info-value">
                  <span class="value-text">{{ formData.location || '未填写' }}</span>
                </span>
              </div>
              <div class="info-item">
                <span class="info-label"><el-icon><Phone /></el-icon> 电话</span>
                <span class="info-value">
                  <span class="value-text">{{ formData.telephone || '未绑定' }}</span>
                  <el-tag v-if="formData.telephone" type="success" class="inline-tag">已绑定</el-tag>
                </span>
              </div>
              <div class="info-item">
                <span class="info-label"><el-icon><Male /></el-icon> 性别</span>
                <span class="info-value">
                  <span class="value-text">{{ getGenderText(formData.gender) }}</span>
                </span>
              </div>

              <div class="info-item full-row">
                <span class="info-label"><el-icon><Document /></el-icon> 个人简介</span>
                <p class="info-value bio-text value-text">{{ formData.bio || '这个人很懒，什么都没留下...' }}</p>
              </div>
            </div>

            <!-- 编辑模式 (带边框的表单) -->
            <el-form 
              v-else
              ref="formRef"
              :model="formData"
              :rules="rules"
              label-width="80px"
              class="profile-edit-form"
            >
              <el-form-item label="全名" prop="nickname">
                <el-input v-model="formData.nickname" placeholder="请输入全名" maxlength="20" show-word-limit />
              </el-form-item>

              <el-form-item label="所在地区" prop="location">
                <el-cascader
                  v-model="selectedLocation"
                  :options="pcaTextArr"
                  placeholder="请选择所在地区"
                  style="width: 100%"
                  clearable
                />
              </el-form-item>

              <el-form-item label="电话号码" prop="telephone">
                <el-input :value="formData.telephone || '未绑定'" disabled />
              </el-form-item>

              <el-form-item label="性别" prop="gender">
                <el-radio-group v-model="formData.gender">
                  <el-radio :value="0">保密</el-radio>
                  <el-radio :value="1">男</el-radio>
                  <el-radio :value="2">女</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="个人简介" prop="bio">
                <el-input 
                  v-model="formData.bio" 
                  type="textarea" 
                  :rows="4" 
                  placeholder="介绍一下你自己吧..." 
                  maxlength="200" 
                  show-word-limit 
                />
              </el-form-item>



              <div class="form-actions">
                <el-button type="primary" :loading="saving" @click="saveProfile">保存修改</el-button>
                <el-button @click="toggleEditMode">取消</el-button>
              </div>
            </el-form>
          </div>
        </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Camera, Select, Warning, Edit, Message, Location, Male, Document, Phone, Calendar } from '@element-plus/icons-vue'
import { pcaTextArr } from 'element-china-area-data'
import userAPI from '@/api/userapi'
import type { UserProfile } from '@/api/userapi'
import { formatTime, getImageUrl } from '@/utils/format'
import { useUserStore } from '@/store/userstore'

const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(true)
const saving = ref(false)
const isEditing = ref(false)

// 选中的地区数组 [省, 市, 区]
const selectedLocation = ref<string[]>([])

// 表单数据
const formData = reactive<Partial<UserProfile>>({
  telephone: '',
  nickname: '',
  avatar: '',
  bio: '',
  gender: 0,
  location: '',
  date_joined: '',
  is_verified: false,
})

// 专门处理头像 URL 的计算方法
const getFullAvatarUrl = computed(() => {
  const avatarPath = formData.avatar
  if (!avatarPath) return 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
  
  if (avatarPath.startsWith('http://') || avatarPath.startsWith('https://')) {
    return avatarPath
  }
  
  return getImageUrl(avatarPath)
})

// 性别文本转换
const getGenderText = (gender?: number) => {
  if (gender === 1) return '男'
  if (gender === 2) return '女'
  return '保密'
}

// 切换编辑模式
const toggleEditMode = () => {
  if (isEditing.value) {
    // 取消编辑时重置表单
    resetForm()
  }
  isEditing.value = !isEditing.value
}

// 保存一份原始数据用于重置
let originalData = {}

// 表单校验规则
const rules = reactive<FormRules>({
  nickname: [
    { required: true, message: '请输入全名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  bio: [
    { max: 200, message: '个人简介不能超过200个字符', trigger: 'blur' }
  ]
})

// 获取用户资料
const fetchProfile = async () => {
  loading.value = true
  try {
    const res = await userAPI.getUserProfileAPI()
    if (res.code === 200 && res.data) {
      Object.assign(formData, res.data)
      originalData = JSON.parse(JSON.stringify(res.data))
      
      // 初始化地区选择器数据
      if (res.data.location) {
        selectedLocation.value = res.data.location.split(' ')
      }

      // 同步更新顶部导航栏的用户信息
      if (res.data.nickname || res.data.avatar) {
        userStore.setLoginState(
          userStore.token, 
          localStorage.getItem('refresh') || '', 
          res.data.nickname || '',
          res.data.avatar || ''
        )
      }
      // 同步更新全局的头像状态，确保右上角导航栏也能实时更新
      if (res.data.avatar && userStore.setAvatar) {
        userStore.setAvatar(res.data.avatar)
      }
    } else {
      ElMessage.error(res.msg || '获取个人资料失败')
    }
  } catch (error) {
    console.error('获取个人资料请求出错:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 保存资料
const saveProfile = async () => {
  if (!formRef.value) return
  
  formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        saving.value = true
        
        // 将级联选择器数组拼接为空格分隔的字符串
        formData.location = selectedLocation.value.join(' ')
        
        // 构造要更新的数据，剔除不可修改的字段
        const updateData = {
          nickname: formData.nickname,
          bio: formData.bio,
          gender: formData.gender,
          location: formData.location,
        }
        
        const res = await userAPI.updateUserProfileAPI(updateData)
        if (res.code === 200) {
          ElMessage.success('个人资料更新成功')
          // 更新原始数据备份
          originalData = JSON.parse(JSON.stringify(formData))
          
          // 更新顶栏显示
          userStore.setLoginState(
            userStore.token, 
            localStorage.getItem('refresh') || '', 
            formData.nickname || '',
            formData.avatar || ''
          )
          
          // 保存成功后退出编辑模式
          isEditing.value = false
        } else {
          ElMessage.error(res.msg || '更新失败')
        }
      } catch (error) {
        console.error('更新个人资料请求失败:', error)
        ElMessage.error('更新个人资料请求失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 重置表单
const resetForm = () => {
  Object.assign(formData, originalData)
  if (formData.location) {
    selectedLocation.value = formData.location.split(' ')
  } else {
    selectedLocation.value = []
  }
  formRef.value?.clearValidate()
}

// 头像上传前的校验
const beforeAvatarUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('上传头像图片只能是图片格式!')
  }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!')
  }
  return isImage && isLt2M
}

// 自定义头像上传
const handleAvatarUpload = async (options: any) => {
  try {
    const formDataObj = new FormData()
    formDataObj.append('file', options.file)
    
    // 第一步：拿到上传接口返回的相对路径
    const res = await userAPI.uploadAvatarAPI(formDataObj)
    
    if (res.code === 200 && res.data && res.data.url) {
      const avatarUrl = res.data.url
      
      // 第二步：立刻调用更新个人资料接口，将头像相对路径提交给后端保存
      const updateRes = await userAPI.updateUserProfileAPI({ avatar: avatarUrl })
      
      if (updateRes.code === 200) {
        ElMessage.success('头像上传成功')
        
        // 第三步：手动将前端本地的响应式变量更新为新的相对路径，触发无感刷新
        formData.avatar = avatarUrl
        
        // 同步更新全局 store，以保证右上角顶栏同步刷新
        if (userStore.setAvatar) {
          userStore.setAvatar(avatarUrl)
        }
      } else {
        ElMessage.error(updateRes.msg || '保存头像信息失败')
      }
    } else {
      ElMessage.error(res.msg || '头像上传失败')
    }
  } catch (error) {
    console.error('头像上传流程出错:', error)
    ElMessage.error('头像上传或保存请求出错')
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped src="@/styles/decorative-background.css"></style>

<style scoped>
.profile-page {
  width: 100%;
  height: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-x: hidden; 
}

.profile-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px); 
  width: 100%; 
  box-sizing: border-box;
  overflow-y: auto; 
  overflow-x: hidden;
  position: relative;
  z-index: 2; /* 确保主要内容层级在泼墨装饰之上 */
}

/* 1. 顶部渐变背景区 */
.profile-header-bg {
  position: absolute; 
  top: 0;
  left: 0;
  right: 0; 
  height: 126px; 
  /* 
    再浅一点点：
    0% (最左边): 较深的一点点蓝 #64a8ff
    30% - 70% (中间): 浅蓝色大面积过渡 #a8d1ff -> #cce3ff
    100% (最右边): 深色蓝 #5b9cf5
  */
  background: linear-gradient(90deg, #64a8ff 0%, #a8d1ff 30%, #cce3ff 60%, #5b9cf5 100%); 
  opacity: 1; 
  z-index: 0; 
}



/* 背景装饰包装器 - 仅占据下方区域 */
.decorative-bg-wrapper {
  position: absolute !important;
  top: 126px; /* 蓝色渐变的高度 */
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0; /* 放在内容区最底层 */
  pointer-events: none; /* 防止挡住用户操作 */
  overflow: hidden;
}

.banner-right {
  position: absolute;
  right: 0px; 
  top: 140px; 
  z-index: 30; 
}

.edit-profile-btn {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  background: #ffffff;
  color: #00796b;
  border: 1px solid #e0e0e0;
  border-radius: 8px; /* 方形，微微圆角 */
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 8px 16px;
}

.profile-user-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 46px; /* 原 100px 减去 54px (背景减少的高度) 得到 46px，保持相对位置 */
  margin-bottom: 32px; 
  padding: 0;
  position: relative;
  z-index: 10;
}

.avatar-wrapper {
  position: relative;
  z-index: 10;
  margin-bottom: 16px;
  /* 去掉 transform 位移，因为我们已经通过 profile-user-header 和绝对背景控制了位置 */
}

.avatar-uploader {
  border-radius: 50%;
  cursor: pointer;
  overflow: hidden;
  border: 4px solid #fff; 
  box-sizing: border-box; 
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); /* 阴影调重一点点，让它在深色背景上凸显 */
  transition: all 0.3s ease;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 108px; 
  height: 108px;
}

/* 保证 element-plus 的内部上传盒子占满并居中 */
.avatar-uploader :deep(.el-upload) {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar-uploader:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.avatar-preview {
  display: block;
  width: 100px !important; /* 强制覆盖组件内置的 width */
  height: 100px !important; /* 强制覆盖组件内置的 height */
  object-fit: cover; 
}

.avatar-placeholder {
  width: 120px;
  height: 120px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #e8f0fe 0%, #f0f0ff 100%);
  border-radius: 50%;
}

.avatar-uploader-icon {
  font-size: 36px;
  color: #a0b4d0;
}

.avatar-hover-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(2px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #fff;
  opacity: 0;
  transition: opacity 0.3s ease;
  font-size: 13px;
  gap: 4px;
}

.avatar-uploader:hover .avatar-hover-mask {
  opacity: 1;
}

.avatar-hover-mask .el-icon {
  font-size: 24px;
}

.edit-profile-btn:hover {
  background: #f1f8f9;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  border-color: #00796b; /* hover时给点颜色反馈 */
}

.profile-layout-inner {
  width: 100%;
  max-width: 1000px; 
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  /* 去掉 flex: 1，不强制拉伸占据底部空间，自然高度即可 */
  position: relative;
}

/* 2. 头像下方信息区 */
.user-summary-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  position: relative; /* 保证不受底层干扰 */
  z-index: 10;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap; /* 如果屏幕很窄，让认证标签换行 */
}

.verified-tag {
  border-color: transparent; 
  font-weight: bold;
  display: inline-flex;
  align-items: center;
  justify-content: center; /* 确保整体居中 */
  height: 24px; /* 给一个固定高度让 flex 对齐 */
  transition: none !important;
  animation: none !important;
  transform: none !important;
}

.tag-content {
  display: flex;
  align-items: center;
  gap: 4px; /* 图标和文字之间的距离 */
  line-height: 1; /* 修正因为行高导致的垂直居中偏移 */
}

.user-nickname {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #303133; /* 改回深灰色，因为蓝色渐变比较短，文字实际渲染在下方白色的区域 */
  letter-spacing: 0.5px;
}

.time-row {
  display: flex;
  align-items: center;
}

.join-time {
  font-size: 14px;
  color: #909399; /* 改回原来的灰色，同样因为它是渲染在下方白色的区域 */
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 3. 下半部分内容区 */
.profile-content-area {
  flex: 1;
  background: transparent; 
  padding: 0 40px; /* 移除底部 padding，通过卡片的 margin-bottom 留白 */
  display: flex;
  justify-content: center;
  align-items: flex-start;
  z-index: 20; 
  position: relative; 
  overflow-x: hidden; 
  overflow-y: hidden; /* 这里也改为 hidden，滚动由全局接管，不单独滚动区域 */
  width: 100%;
  box-sizing: border-box;
}

/* 移除 no-scroll 类关联的样式，完全交由全局滚动 */

/* 干净的白色卡片 */
.info-card {
  width: 100%;
  /* 恢复纯净的白色背景以搭配你原来的 CSS 泼墨效果 */
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px; 
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06); 
  padding: 32px 40px; 
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 10;
  box-sizing: border-box; 
  overflow: visible; 
  margin-bottom: 40px; 
}



.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px; /* 缩小边距 */
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

/* 只读态网格布局 */
.info-readonly-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px 40px; /* 增加列之间的横向间距，利用更大的宽度 */
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #fafafa;
  padding: 16px 24px; /* 增加每个项的内边距，使内部不那么拥挤 */
  border-radius: 12px;
}

.full-row {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 13px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-label .el-icon {
  font-size: 15px;
  color: #a8abb2;
}

.info-value {
  font-size: 15px;
  color: #303133;
  font-weight: 600;
  min-height: 22px;
  display: flex;
  align-items: center;
  justify-content: space-between; /* 让内容和右侧标签分居两端 */
  gap: 8px;
}

.value-text {
  flex: 1; /* 占据剩余空间 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis; /* 长文本截断，防止撑开影响右对齐标签 */
}

.inline-tag {
  margin-left: auto; /* 强制靠右 */
  transition: none !important;
  animation: none !important;
  transform: none !important;
}

.bio-text {
  font-weight: 400;
  line-height: 1.6;
  white-space: pre-wrap; /* 覆盖掉 value-text 上的 nowrap，让简介可以换行 */
  word-break: break-all;
  overflow: visible; /* 恢复显示 */
  text-overflow: clip; /* 恢复 */
}

/* 编辑态表单 */
.profile-edit-form {
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  /* 去掉 flex: 1 让它自然高度 */
}

.profile-edit-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.profile-edit-form :deep(.el-input__wrapper),
.profile-edit-form :deep(.el-textarea__inner) {
  background-color: #f8f9fb;
  border-color: transparent;
  box-shadow: none;
  transition: all 0.3s ease;
}

.profile-edit-form :deep(.el-input__wrapper:hover),
.profile-edit-form :deep(.el-input__wrapper.is-focus),
.profile-edit-form :deep(.el-textarea__inner:hover),
.profile-edit-form :deep(.el-textarea__inner:focus) {
  background-color: #fff;
  box-shadow: 0 0 0 1px #409eff inset;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px; /* 改回固定外边距，不需要 push 到底 */
}

.form-actions .el-button {
  padding: 8px 24px;
}

@media (max-width: 768px) {
  .info-readonly-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .info-card {
    padding: 20px;
  }
  
  .profile-user-header {
    margin-top: -40px;
    padding: 0 10px;
  }
  
  .banner-right {
    right: 20px;
  }
}
</style>
