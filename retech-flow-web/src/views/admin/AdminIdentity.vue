<template>
  <section class="admin-table-page">
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="搜索邮箱、昵称、姓名或身份证号" clearable @keyup.enter="loadList" />
      <el-select v-model="query.status" placeholder="审核状态" @change="loadList">
        <el-option label="待审核" :value="1" />
        <el-option label="已通过" :value="2" />
        <el-option label="已驳回" :value="3" />
        <el-option label="全部" value="all" />
      </el-select>
      <el-button type="primary" @click="loadList">查询</el-button>
    </div>

    <el-table v-loading="loading" :data="list" class="data-table" empty-text="暂无数据">
      <el-table-column label="用户" min-width="240">
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
      <el-table-column label="真实姓名" prop="real_name" width="140" />
      <el-table-column label="身份证号" min-width="220">
        <template #default="{ row }">
          <span class="id-card">{{ row.id_card || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="verifyTagType(row.verification_status)">
            {{ row.verification_status_text || verifyStatusText(row.verification_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="驳回原因" min-width="180">
        <template #default="{ row }">
          <span class="reject-reason">{{ row.verification_reject_reason || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.verification_status === 1" size="small" type="success" @click="reviewIdentity(row, 'approve')">
            通过
          </el-button>
          <el-button v-if="row.verification_status === 1" size="small" type="danger" plain @click="reviewIdentity(row, 'reject')">
            驳回
          </el-button>
          <span v-else class="done-text">已处理</span>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      layout="prev, pager, next, total"
      :total="total"
      :page-size="query.page_size"
      @current-change="changePage"
    />
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
const query = reactive({ page: 1, page_size: 10, status: 1 as any, keyword: '' })

const verifyStatusText = (status: number) => ({ 0: '未提交', 1: '待审核', 2: '已通过', 3: '已驳回' } as Record<number, string>)[status] || '未知'
const verifyTagType = (status: number) => ({ 1: 'warning', 2: 'success', 3: 'danger' } as Record<number, any>)[status] || 'info'

const loadList = async () => {
  loading.value = true
  try {
    const res = await adminApi.getIdentityReviews(query)
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

const reviewIdentity = async (row: any, action: 'approve' | 'reject') => {
  let reason = ''
  if (action === 'reject') {
    const result = await ElMessageBox.prompt('请输入实名认证驳回原因', '驳回实名认证', {
      confirmButtonText: '确认驳回',
      cancelButtonText: '取消',
      inputPattern: /\S+/,
      inputErrorMessage: '请填写驳回原因',
    })
    reason = result.value
  }
  await adminApi.reviewUserIdentity(row.id, action, reason)
  ElMessage.success(action === 'approve' ? '实名认证已通过' : '实名认证已驳回')
  loadList()
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
  max-width: 320px;
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

.id-card {
  font-family: Consolas, 'Courier New', monospace;
}

.reject-reason {
  color: #dc2626;
}

.done-text {
  color: #64748b;
  font-size: 13px;
}

.data-table {
  margin-bottom: 14px;
}
</style>
