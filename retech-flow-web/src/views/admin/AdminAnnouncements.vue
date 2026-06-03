<template>
  <section class="notice-page">
    <div class="toolbar">
      <div>
        <h3>公告管理</h3>
        <p>发布平台公告，用户可在“我的消息”的系统消息中查看。</p>
      </div>
      <el-button type="primary" @click="openDialog()">发布公告</el-button>
    </div>

    <el-table v-loading="loading" :data="list" empty-text="暂无数据" class="data-table">
      <el-table-column label="公告" min-width="260">
        <template #default="{ row }">
          <div class="notice-title">
            <strong>{{ row.title }}</strong>
            <span>{{ row.content }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '展示中' : '已停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="发布人" prop="publisher" width="130" />
      <el-table-column label="发布时间" width="180">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="210" fixed="right">
        <template #default="{ row }">
          <el-button size="small" plain @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" plain @click="deleteNotice(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      layout="prev, pager, next, total"
      :total="total"
      :page-size="query.page_size"
      @current-change="changePage"
    />

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑公告' : '发布公告'" width="560px">
      <el-form label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入公告标题" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="6" placeholder="请输入公告内容" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="展示" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNotice">{{ form.id ? '保存' : '发布' }}</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import adminApi from '@/api/adminapi'

const loading = ref(false)
const dialogVisible = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10 })
const form = reactive({ id: 0, title: '', content: '', is_active: true })

const loadList = async () => {
  loading.value = true
  try {
    const res = await adminApi.getAnnouncements(query)
    list.value = res.data.list || []
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const changePage = (page: number) => {
  query.page = page
  loadList()
}

const openDialog = (row?: any) => {
  form.id = row?.id || 0
  form.title = row?.title || ''
  form.content = row?.content || ''
  form.is_active = row?.is_active ?? true
  dialogVisible.value = true
}

const saveNotice = async () => {
  const payload = {
    title: form.title.trim(),
    content: form.content.trim(),
    is_active: form.is_active,
  }
  if (!payload.title || !payload.content) {
    ElMessage.warning('请填写公告标题和内容')
    return
  }
  if (form.id) await adminApi.updateAnnouncement(form.id, payload)
  else await adminApi.createAnnouncement(payload)
  ElMessage.success(form.id ? '公告已更新' : '公告已发布')
  dialogVisible.value = false
  loadList()
}

const deleteNotice = async (row: any) => {
  await ElMessageBox.confirm(`确认删除公告「${row.title}」吗？`, '删除公告', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
  await adminApi.deleteAnnouncement(row.id)
  ElMessage.success('公告已删除')
  loadList()
}

const formatDate = (value: string) => {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

onMounted(loadList)
</script>

<style scoped>
.notice-page {
  padding: 16px;
  border: 1px solid #e3eaf3;
  border-radius: 8px;
  background: #fff;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
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

.notice-title strong,
.notice-title span {
  display: block;
}

.notice-title span {
  overflow: hidden;
  margin-top: 5px;
  color: #64748b;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.data-table {
  margin-bottom: 14px;
}
</style>
