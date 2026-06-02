<template>
  <DecorativeBackground>
  <div class="address-container">
    <div class="address-header">
      <div class="header-text">
        <h2>地址管理</h2>
        <p class="subtitle">管理您的收发货地址，可设置默认地址</p>
      </div>
      <el-button type="primary" @click="openAddDialog" :icon="Plus">
        新增地址
      </el-button>
    </div>

    <!-- 地址列表区域 -->
    <el-card class="address-card" shadow="never" v-loading="loading">
      <template v-if="addressList.length > 0">
        <div class="address-list">
          <div 
            class="address-item" 
            v-for="item in addressList" 
            :key="item.id"
          >
            <div class="address-content">
              <div class="address-title">
                <span class="receiver-name">{{ item.receiver_name }}</span>
                <span class="telephone">{{ item.telephone }}</span>
                <el-tag size="small" type="danger" v-if="item.is_default" class="default-tag">默认收货</el-tag>
                <el-tag size="small" type="warning" v-if="item.is_default_return" class="default-tag">默认退发货</el-tag>
              </div>
              <div class="address-detail">
                {{ item.province }} {{ item.city }} {{ item.district }} {{ item.detail_address }}
              </div>
            </div>
            <!-- 操作区 -->
            <div class="address-actions">
              <el-button type="primary" link @click="openEditDialog(item)">编辑</el-button>
            </div>
          </div>
        </div>
      </template>
      <el-empty v-else description="暂无地址，快去添加一个吧~" />
    </el-card>

    <!-- 新增/编辑地址弹窗 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '修改地址' : '新增地址'" 
      width="500px" 
      destroy-on-close
    >
      <el-form 
        ref="formRef" 
        :model="formData" 
        :rules="rules" 
        label-width="100px"
        class="address-form"
      >
        <el-form-item label="收货人" prop="receiver_name">
          <el-input v-model="formData.receiver_name" placeholder="请填写真实姓名" />
        </el-form-item>
        
        <el-form-item label="手机号码" prop="telephone">
          <el-input v-model="formData.telephone" placeholder="请填写手机号码" maxlength="11" />
        </el-form-item>

        <el-form-item label="所在地区" prop="area">
          <el-cascader
            v-model="formData.area"
            :options="pcaTextArr"
            placeholder="请选择省/市/区"
            class="w-full"
            clearable
          />
        </el-form-item>

        <el-form-item label="详细地址" prop="detail_address">
          <el-input 
            v-model="formData.detail_address" 
            type="textarea" 
            :rows="3" 
            placeholder="街道、楼牌号等详细信息" 
          />
        </el-form-item>

        <el-form-item label="设置默认">
          <div class="switch-group">
            <el-checkbox v-model="formData.is_default">设为默认收货地址</el-checkbox>
            <el-checkbox v-model="formData.is_default_return">设为默认退发货地址</el-checkbox>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAdd" :loading="submitting">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
  </DecorativeBackground>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { pcaTextArr } from 'element-china-area-data'
import userAPI from '@/api/userapi'
import type { AddressData } from '@/api/userapi'
import DecorativeBackground from '@/components/DecorativeBackground.vue'

const loading = ref(false)
const addressList = ref<AddressData[]>([])

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const isEdit = ref(false) // 区分新增还是修改
const editId = ref<number | null>(null) // 记录当前修改的地址ID

// 表单结构，用 area 数组暂存省市区
const formData = reactive({
  receiver_name: '',
  telephone: '',
  area: [] as string[],
  detail_address: '',
  is_default: false,
  is_default_return: false
})

const rules = reactive<FormRules>({
  receiver_name: [
    { required: true, message: '请填写收货人姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  telephone: [
    { required: true, message: '请填写手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  area: [
    { required: true, type: 'array', message: '请选择所在地区', trigger: 'change' }
  ],
  detail_address: [
    { required: true, message: '请填写详细地址', trigger: 'blur' },
    { min: 5, max: 100, message: '详细地址长度在 5 到 100 个字符', trigger: 'blur' }
  ]
})

// 获取地址列表
const fetchAddressList = async () => {
  loading.value = true
  try {
    const res = await userAPI.getAddressListAPI()
    if (res.code === 200) {
      addressList.value = res.data
    } else {
      ElMessage.error(res.msg || '获取地址列表失败')
    }
  } catch (error) {
    console.error('获取地址列表出错:', error)
    ElMessage.error('网络请求失败')
  } finally {
    loading.value = false
  }
}

// 打开新增弹窗
const openAddDialog = () => {
  isEdit.value = false
  editId.value = null
  
  formData.receiver_name = ''
  formData.telephone = ''
  formData.area = []
  formData.detail_address = ''
  formData.is_default = false
  formData.is_default_return = false
  
  dialogVisible.value = true
}

// 打开编辑弹窗（回显数据）
const openEditDialog = (row: AddressData) => {
  isEdit.value = true
  editId.value = row.id || null
  
  // 深拷贝赋值，防止修改表单时直接影响到列表数据
  const data = JSON.parse(JSON.stringify(row))
  
  formData.receiver_name = data.receiver_name
  formData.telephone = data.telephone
  // 还原省市区级联数组
  formData.area = [data.province, data.city, data.district].filter(Boolean)
  formData.detail_address = data.detail_address
  formData.is_default = data.is_default
  formData.is_default_return = data.is_default_return
  
  dialogVisible.value = true
}

// 提交（新增或修改）
const submitAdd = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      
      // 组装后端需要的数据格式
      const submitData: AddressData = {
        receiver_name: formData.receiver_name,
        telephone: formData.telephone,
        province: formData.area[0] || '',
        city: formData.area[1] || '',
        district: formData.area[2] || '',
        detail_address: formData.detail_address,
        is_default: formData.is_default,
        is_default_return: formData.is_default_return
      }

      try {
        if (isEdit.value && editId.value) {
          // 执行修改逻辑
          const res = await userAPI.updateAddressAPI(editId.value, submitData)
          if (res.code === 200) {
            ElMessage.success('修改成功')
            dialogVisible.value = false
            fetchAddressList() // 刷新列表
          } else {
            ElMessage.error(res.msg || '修改失败')
          }
        } else {
          // 执行新增逻辑
          const res = await userAPI.addAddressAPI(submitData)
          if (res.code === 200) {
            ElMessage.success('地址添加成功')
            dialogVisible.value = false
            fetchAddressList() // 刷新列表
          } else {
            ElMessage.error(res.msg || '地址添加失败')
          }
        }
      } catch (error) {
        console.error('操作地址出错:', error)
        ElMessage.error('网络请求失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  fetchAddressList()
})
</script>

<style scoped>
.address-container {
  flex: 1;
  padding: 28px;
  display: flex;
  flex-direction: column;
}

.address-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.address-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #303133;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.address-card {
  flex: 1;
  border-radius: 12px;
  border: 1px solid #ebeef5;
}

.address-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.address-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.address-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.receiver-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.telephone {
  font-size: 15px;
  color: #606266;
  font-family: monospace;
}

.default-tag {
  border-radius: 4px;
  transition: none !important;
  animation: none !important;
  transform: none !important;
}

.address-detail {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.w-full {
  width: 100%;
}

.switch-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
