<template>
  <section class="admin-table-page">
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="搜索邮箱或昵称" clearable @keyup.enter="loadList" />
      <el-select v-model="query.role" placeholder="角色" @change="loadList">
        <el-option label="全部" value="all" />
        <el-option label="普通用户" :value="1" />
        <el-option label="平台审核员" :value="2" />
        <el-option label="系统管理员" :value="3" />
      </el-select>
      <el-button type="primary" @click="loadList">查询</el-button>
    </div>

    <el-table v-loading="loading" :data="list" class="data-table" empty-text="暂无数据">
      <el-table-column label="用户" min-width="250">
        <template #default="{ row }">
          <div class="user-cell">
            <el-avatar :size="36" :src="getImageUrl(row.avatar)" />
            <div>
              <strong>{{ row.nickname || '未命名用户' }}</strong>
              <span>{{ row.email }}</span>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="角色" width="180">
        <template #default="{ row }">
          <div class="role-cell">
            <el-tag>{{ roleText(row.role) }}</el-tag>
            <el-button link type="primary" @click="openRoleDialog(row)">修改</el-button>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '正常' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="balance" label="余额" width="110" />
      <el-table-column label="注册时间" width="180">
        <template #default="{ row }">{{ formatDate(row.date_joined) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button size="small" plain @click="resetPassword(row)">重置密码</el-button>
          <el-button size="small" :type="row.is_active ? 'danger' : 'success'" plain @click="toggleActive(row)">
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      layout="prev, pager, next, total"
      :total="total"
      :page-size="query.page_size"
      @current-change="changePage"
    />

    <el-dialog v-model="roleDialogVisible" title="修改用户角色" width="420px">
      <el-form label-width="80px">
        <el-form-item label="用户">
          <span>{{ currentRoleUser?.nickname || currentRoleUser?.email || '-' }}</span>
        </el-form-item>
        <el-form-item label="当前角色">
          <span>{{ roleText(currentRoleUser?.role) }}</span>
        </el-form-item>
        <el-form-item label="新角色">
          <el-select v-model="roleForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="普通用户" :value="1" />
            <el-option label="平台审核员" :value="2" />
            <el-option label="系统管理员" :value="3" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="!!changingRoleId" @click="confirmRoleChange">确认调整</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import adminApi from '@/api/adminapi'
import { getImageUrl } from '@/utils/format'

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const changingRoleId = ref('')
const roleDialogVisible = ref(false)
const currentRoleUser = ref<any>(null)
const roleForm = reactive({ role: 1 })
const query = reactive({ page: 1, page_size: 10, role: 'all' as any, keyword: '' })

const roleText = (role: number | string | undefined) => {
  return ({ 1: '普通用户', 2: '平台审核员', 3: '系统管理员' } as Record<number, string>)[Number(role)] || '未知角色'
}

const loadList = async () => {
  loading.value = true
  try {
    const res = await adminApi.getUsers(query)
    list.value = (res.data.list || []).map((item: any) => ({ ...item, role: Number(item.role) }))
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const changePage = (page: number) => {
  query.page = page
  loadList()
}

const openRoleDialog = (row: any) => {
  currentRoleUser.value = row
  roleForm.role = Number(row.role)
  roleDialogVisible.value = true
}

const confirmRoleChange = async () => {
  const row = currentRoleUser.value
  if (!row) return
  const oldRole = Number(row.role)
  const role = Number(roleForm.role)
  if (oldRole === role) {
    roleDialogVisible.value = false
    return
  }
  try {
    await ElMessageBox.confirm(
      `确认把「${row.nickname || row.email}」从「${roleText(oldRole)}」调整为「${roleText(role)}」吗？`,
      '确认切换角色',
      {
        confirmButtonText: '确认调整',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
    changingRoleId.value = row.id
    await adminApi.updateUserRole(row.id, role)
    ElMessage.success('角色已更新')
    roleDialogVisible.value = false
    await loadList()
  } catch (error) {
    if (changingRoleId.value) row.role = oldRole
  } finally {
    changingRoleId.value = ''
  }
}

const resetPassword = async (row: any) => {
  const result = await ElMessageBox.prompt(`请输入「${row.nickname || row.email}」的新密码`, '重置用户密码', {
    confirmButtonText: '确认重置',
    cancelButtonText: '取消',
    inputType: 'password',
    inputPattern: /^.{6,}$/,
    inputErrorMessage: '密码至少 6 位',
  })
  await adminApi.resetUserPassword(row.id, result.value)
  ElMessage.success('用户密码已重置')
}

const toggleActive = async (row: any) => {
  await ElMessageBox.confirm(
    `确认${row.is_active ? '禁用' : '启用'}「${row.nickname || row.email}」吗？`,
    '确认用户状态',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning',
    },
  )
  await adminApi.updateUserStatus(row.id, !row.is_active)
  ElMessage.success('用户状态已更新')
  loadList()
}

const formatDate = (value: string) => {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

onMounted(loadList)
</script>

<style scoped>
.admin-table-page {
  padding: 16px;
  border: 1px solid #e3eaf3;
  border-radius: 8px;
  background: #fff;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.toolbar .el-input {
  max-width: 280px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-cell strong,
.user-cell span {
  display: block;
}

.user-cell span {
  margin-top: 4px;
  color: #64748b;
  font-size: 12px;
}

.role-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.data-table {
  margin-bottom: 14px;
}
</style>
