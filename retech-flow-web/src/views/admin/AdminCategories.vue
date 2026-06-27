<template>
  <section class="config-page" v-loading="loading">
    <div class="toolbar">
      <div>
        <h3>机型分类库</h3>
        <p>维护发布商品时可选的分类、规格字段和标准选项。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCategoryDialog()">新增分类</el-button>
    </div>

    <div class="category-grid">
      <article v-for="category in categories" :key="category.id" class="category-card">
        <header>
          <div class="category-heading">
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
            <div class="attr-content">
              <b>{{ attr.name }}</b>
              <div v-if="attr.options?.length" class="option-preview">
                <span v-for="option in attr.options" :key="option">{{ option }}</span>
              </div>
              <span v-else class="empty-options">暂无选项</span>
            </div>
            <div class="actions">
              <el-button size="small" plain @click="openAttributeDialog(category, attr)">编辑</el-button>
              <el-button size="small" type="danger" plain @click="deleteAttribute(category, attr)">删除</el-button>
            </div>
          </div>
          <el-empty v-if="!category.attributes?.length" description="暂无属性" :image-size="70" />
        </div>

        <el-button class="add-attr" plain :icon="Plus" @click="openAttributeDialog(category)">新增属性</el-button>
      </article>
    </div>

    <el-dialog v-model="categoryDialogVisible" :title="categoryForm.id ? '编辑分类' : '新增分类'" width="420px">
      <el-form label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="categoryForm.name" maxlength="20" placeholder="例如：智能手机" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="categoryForm.sort" :min="0" :max="999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="attrDialogVisible"
      :title="attrForm.id ? '编辑属性' : '新增属性'"
      width="560px"
      class="attribute-dialog"
    >
      <el-form label-width="82px">
        <el-form-item label="属性名称">
          <el-input v-model="attrForm.name" maxlength="20" placeholder="例如：运行内存" />
        </el-form-item>
        <el-form-item label="选项">
          <div class="option-editor">
            <div class="option-input-row">
              <el-input
                v-model="newOption"
                maxlength="40"
                placeholder="输入一个选项后按回车"
                @keyup.enter="addOption"
                @paste="handleOptionPaste"
              />
              <el-button type="primary" :icon="Plus" @click="addOption">添加</el-button>
            </div>
            <div class="option-tags" :class="{ empty: attrOptions.length === 0 }">
              <el-tag
                v-for="option in attrOptions"
                :key="option"
                closable
                effect="plain"
                @close="removeOption(option)"
              >
                {{ option }}
              </el-tag>
              <span v-if="attrOptions.length === 0">尚未添加选项</span>
            </div>
            <small>可一次粘贴多项，使用逗号或换行分隔；重复项会自动忽略。</small>
          </div>
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
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import adminApi from '@/api/adminapi'

const loading = ref(false)
const categories = ref<any[]>([])
const categoryDialogVisible = ref(false)
const attrDialogVisible = ref(false)
const currentCategoryId = ref<number | null>(null)
const attrOptions = ref<string[]>([])
const newOption = ref('')

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
  attrOptions.value = [...(attr?.options || [])]
  newOption.value = ''
  attrDialogVisible.value = true
}

const appendOptions = (values: string[]) => {
  const normalized = values.map(item => item.trim()).filter(Boolean)
  const existing = new Set(attrOptions.value.map(item => item.toLocaleLowerCase()))
  normalized.forEach((item) => {
    const key = item.toLocaleLowerCase()
    if (!existing.has(key)) {
      attrOptions.value.push(item)
      existing.add(key)
    }
  })
}

const addOption = () => {
  appendOptions(newOption.value.split(/[\n,，;；]+/))
  newOption.value = ''
}

const handleOptionPaste = (event: ClipboardEvent) => {
  const text = event.clipboardData?.getData('text') || ''
  if (!/[\n,，;；]/.test(text)) return
  event.preventDefault()
  appendOptions(text.split(/[\n,，;；]+/))
  newOption.value = ''
}

const removeOption = (option: string) => {
  attrOptions.value = attrOptions.value.filter(item => item !== option)
}

const saveAttribute = async () => {
  if (!currentCategoryId.value) return
  addOption()
  const payload = {
    name: attrForm.name.trim(),
    options: [...attrOptions.value],
  }
  if (!payload.name) {
    ElMessage.warning('请填写属性名称')
    return
  }
  if (!payload.options.length) {
    ElMessage.warning('请至少添加一个选项')
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
  color: #172033;
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
  align-items: start;
}

.category-card {
  display: flex;
  box-sizing: border-box;
  height: 520px;
  min-width: 0;
  flex-direction: column;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
}

.category-card header,
.attr-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.category-card header {
  flex: 0 0 auto;
  min-height: 44px;
  padding-bottom: 14px;
  border-bottom: 1px solid #edf2f7;
}

.category-heading,
.attr-content {
  min-width: 0;
}

.category-card strong,
.attr-item b,
.category-card span,
.attr-item span {
  display: block;
}

.category-card span {
  margin-top: 4px;
  color: #64748b;
  font-size: 12px;
}

.actions {
  display: flex;
  flex-shrink: 0;
  gap: 8px;
}

.actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.attr-list {
  display: flex;
  min-height: 0;
  flex: 1 1 auto;
  flex-direction: column;
  gap: 0;
  margin: 8px 0 12px;
  padding-right: 4px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.attr-list::-webkit-scrollbar {
  width: 5px;
}

.attr-list::-webkit-scrollbar-thumb {
  border-radius: 5px;
  background: #d7e0eb;
}

.attr-item {
  padding: 12px 4px;
  border-bottom: 1px solid #edf2f7;
}

.attr-item:last-child {
  border-bottom: 0;
}

.attr-item b {
  color: #172033;
  font-size: 14px;
}

.option-preview {
  display: flex;
  max-height: 46px;
  flex-wrap: wrap;
  gap: 4px 6px;
  margin-top: 7px;
  overflow: hidden;
}

.option-preview span {
  margin: 0;
  color: #64748b;
  line-height: 1.45;
}

.option-preview span:not(:last-child)::after {
  content: " /";
  color: #c0cad7;
}

.empty-options {
  margin-top: 7px !important;
  color: #94a3b8 !important;
}

.add-attr {
  width: 100%;
  flex: 0 0 auto;
}

.option-editor {
  display: grid;
  width: 100%;
  gap: 10px;
}

.option-input-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
}

.option-tags {
  display: flex;
  min-height: 92px;
  max-height: 210px;
  align-content: flex-start;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: #fafcff;
}

.option-tags.empty {
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 13px;
}

.option-tags :deep(.el-tag) {
  max-width: 100%;
}

.option-tags :deep(.el-tag__content) {
  overflow: hidden;
  text-overflow: ellipsis;
}

.option-editor small {
  color: #94a3b8;
  font-size: 12px;
  line-height: 1.5;
}

@media (max-width: 1000px) {
  .category-grid {
    grid-template-columns: 1fr;
  }

  .category-card {
    height: min(520px, calc(100dvh - 150px));
    min-height: 420px;
  }
}

@media (max-width: 640px) {
  .toolbar {
    align-items: flex-start;
    gap: 12px;
  }

  .category-card header {
    flex-direction: column;
  }

  .attribute-dialog :deep(.el-dialog) {
    width: calc(100vw - 24px) !important;
  }
}
</style>
