<template>
  <section class="config-page" v-loading="loading">
    <div class="toolbar">
      <div>
        <h3>机型分类库</h3>
        <p>维护发布商品时可选的分类、规格字段和标准选项。</p>
      </div>
      <el-button type="primary" @click="openCategoryDialog()">新增分类</el-button>
    </div>

    <div class="category-grid">
      <article v-for="category in categories" :key="category.id" class="category-card">
        <header>
          <div>
            <strong>{{ category.name }}</strong>
            <span>排序 {{ category.sort }} · {{ category.goods_count || 0 }} 个商品</span>
          </div>
          <div class="actions">
            <el-button size="small" plain @click="openCategoryDialog(category)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="deleteCategory(category)">删除</el-button>
          </div>
        </header>

        <div class="attr-list">
          <div v-for="attr in category.attributes" :key="attr.id" class="attr-item">
            <div>
              <b>{{ attr.name }}</b>
              <span>{{ attr.options?.join(' / ') || '暂无选项' }}</span>
            </div>
            <div class="actions">
              <el-button size="small" plain @click="openAttributeDialog(category, attr)">编辑</el-button>
              <el-button size="small" type="danger" plain @click="deleteAttribute(category, attr)">删除</el-button>
            </div>
          </div>
          <el-empty v-if="!category.attributes?.length" description="暂无属性" :image-size="70" />
        </div>

        <el-button class="add-attr" plain @click="openAttributeDialog(category)">新增属性</el-button>
      </article>
    </div>

    <el-dialog v-model="categoryDialogVisible" :title="categoryForm.id ? '编辑分类' : '新增分类'" width="420px">
      <el-form label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="categoryForm.name" placeholder="例如 手机、笔记本、相机" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="categoryForm.sort" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="attrDialogVisible" :title="attrForm.id ? '编辑属性' : '新增属性'" width="520px">
      <el-form label-width="90px">
        <el-form-item label="属性名称">
          <el-input v-model="attrForm.name" placeholder="例如 品牌、内存、成色" />
        </el-form-item>
        <el-form-item label="选项">
          <el-input
            v-model="attrOptionsText"
            type="textarea"
            :rows="4"
            placeholder="每行一个选项，例如 Apple、华为、小米"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="attrDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAttribute">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import adminApi from '@/api/adminapi'

const loading = ref(false)
const categories = ref<any[]>([])
const categoryDialogVisible = ref(false)
const attrDialogVisible = ref(false)
const currentCategoryId = ref<number | null>(null)
const attrOptionsText = ref('')

const categoryForm = reactive({ id: 0, name: '', sort: 0 })
const attrForm = reactive({ id: 0, name: '' })

const loadCategories = async () => {
  loading.value = true
  try {
    const res = await adminApi.getCategories()
    categories.value = res.data || []
  } finally {
    loading.value = false
  }
}

const openCategoryDialog = (category?: any) => {
  categoryForm.id = category?.id || 0
  categoryForm.name = category?.name || ''
  categoryForm.sort = category?.sort || 0
  categoryDialogVisible.value = true
}

const saveCategory = async () => {
  const payload = { name: categoryForm.name.trim(), sort: categoryForm.sort }
  if (!payload.name) {
    ElMessage.warning('请填写分类名称')
    return
  }
  if (categoryForm.id) await adminApi.updateCategory(categoryForm.id, payload)
  else await adminApi.createCategory(payload)
  ElMessage.success('分类已保存')
  categoryDialogVisible.value = false
  loadCategories()
}

const deleteCategory = async (category: any) => {
  await ElMessageBox.confirm(`确认删除分类「${category.name}」吗？`, '删除分类', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
  await adminApi.deleteCategory(category.id)
  ElMessage.success('分类已删除')
  loadCategories()
}

const openAttributeDialog = (category: any, attr?: any) => {
  currentCategoryId.value = category.id
  attrForm.id = attr?.id || 0
  attrForm.name = attr?.name || ''
  attrOptionsText.value = (attr?.options || []).join('\n')
  attrDialogVisible.value = true
}

const saveAttribute = async () => {
  if (!currentCategoryId.value) return
  const payload = {
    name: attrForm.name.trim(),
    options: attrOptionsText.value.split(/\r?\n/).map(item => item.trim()).filter(Boolean),
  }
  if (!payload.name) {
    ElMessage.warning('请填写属性名称')
    return
  }
  if (attrForm.id) await adminApi.updateCategoryAttribute(currentCategoryId.value, attrForm.id, payload)
  else await adminApi.createCategoryAttribute(currentCategoryId.value, payload)
  ElMessage.success('属性已保存')
  attrDialogVisible.value = false
  loadCategories()
}

const deleteAttribute = async (category: any, attr: any) => {
  await ElMessageBox.confirm(`确认删除属性「${attr.name}」吗？`, '删除属性', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
  await adminApi.deleteCategoryAttribute(category.id, attr.id)
  ElMessage.success('属性已删除')
  loadCategories()
}

onMounted(loadCategories)
</script>

<style scoped>
.config-page {
  min-height: 400px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
}

.toolbar h3 {
  margin: 0 0 5px;
  font-size: 18px;
}

.toolbar p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.category-card {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
}

.category-card header,
.attr-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.category-card strong,
.attr-item b,
.category-card span,
.attr-item span {
  display: block;
}

.category-card span,
.attr-item span {
  margin-top: 4px;
  color: #64748b;
  font-size: 12px;
}

.actions {
  display: flex;
  flex-shrink: 0;
  gap: 8px;
}

.attr-list {
  display: grid;
  gap: 10px;
  margin: 16px 0;
}

.attr-item {
  padding: 12px;
  border-radius: 8px;
  background: #f8fafc;
}

.add-attr {
  width: 100%;
}

@media (max-width: 1000px) {
  .category-grid {
    grid-template-columns: 1fr;
  }
}
</style>
