<template>
  <section class="review-page">
    <header class="page-head">
      <div><h2>实名认证审核</h2><p>核对用户姓名与身份证号码，敏感信息仅在详情中完整展示</p></div>
      <div class="head-count"><strong>{{ total }}</strong><span>条记录</span></div>
    </header>

    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="搜索邮箱、昵称、姓名或身份证号" clearable @keyup.enter="search">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="query.status" placeholder="审核状态" @change="search">
        <el-option label="待审核" :value="1" /><el-option label="已通过" :value="2" />
        <el-option label="已驳回" :value="3" /><el-option label="全部状态" value="all" />
      </el-select>
      <el-button type="primary" @click="search">查询</el-button>
      <el-button :icon="Refresh" circle title="刷新" @click="loadList" />
    </div>

    <el-table v-loading="loading" :data="list" class="data-table" empty-text="暂无认证记录">
      <el-table-column label="用户" min-width="250">
        <template #default="{ row }"><div class="user-cell"><el-avatar :size="38" :src="getImageUrl(row.avatar)" /><div><strong>{{ row.nickname || '未命名用户' }}</strong><span>{{ row.email }}</span></div></div></template>
      </el-table-column>
      <el-table-column label="真实姓名" prop="real_name" width="140" />
      <el-table-column label="身份证号" min-width="190"><template #default="{ row }"><span class="id-card">{{ maskIdCard(row.id_card) }}</span></template></el-table-column>
      <el-table-column label="状态" width="110"><template #default="{ row }"><el-tag :type="verifyTagType(row.verification_status)">{{ row.verification_status_text || verifyStatusText(row.verification_status) }}</el-tag></template></el-table-column>
      <el-table-column label="驳回原因" min-width="180" show-overflow-tooltip><template #default="{ row }"><span :class="{ 'reject-reason': row.verification_reject_reason }">{{ row.verification_reject_reason || '-' }}</span></template></el-table-column>
      <el-table-column label="操作" width="230" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" :icon="View" @click="openDetail(row)">查看详情</el-button>
          <el-button v-if="row.verification_status === 1" link type="success" @click="approveIdentity(row)">通过</el-button>
          <el-button v-if="row.verification_status === 1" link type="danger" @click="rejectIdentity(row)">驳回</el-button>
        </template>
      </el-table-column>
    </el-table>

    <footer class="table-footer"><span>共 {{ total }} 条</span><el-pagination v-model:current-page="query.page" layout="prev, pager, next" :total="total" :page-size="query.page_size" @current-change="loadList" /></footer>

    <el-dialog v-model="detailVisible" title="实名认证资料" width="520px" destroy-on-close>
      <div v-if="currentUser" class="identity-detail">
        <div class="identity-user"><el-avatar :size="48" :src="getImageUrl(currentUser.avatar)" /><div><h3>{{ currentUser.nickname || '未命名用户' }}</h3><p>{{ currentUser.email }}</p></div><el-tag :type="verifyTagType(currentUser.verification_status)">{{ currentUser.verification_status_text || verifyStatusText(currentUser.verification_status) }}</el-tag></div>
        <dl><div><dt>真实姓名</dt><dd>{{ currentUser.real_name || '-' }}</dd></div><div><dt>身份证号码</dt><dd class="id-card">{{ currentUser.id_card || '-' }}</dd></div></dl>
        <div v-if="currentUser.verification_reject_reason" class="reason"><b>驳回原因</b><p>{{ currentUser.verification_reject_reason }}</p></div>
        <p class="privacy-note">请仅将身份信息用于平台实名认证审核。</p>
      </div>
      <template #footer><el-button @click="detailVisible = false">关闭</el-button><el-button v-if="currentUser?.verification_status === 1" type="danger" plain @click="rejectIdentity(currentUser)">驳回</el-button><el-button v-if="currentUser?.verification_status === 1" type="primary" @click="approveIdentity(currentUser)">确认通过</el-button></template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search, View } from '@element-plus/icons-vue'
import adminApi from '@/api/adminapi'
import { getImageUrl } from '@/utils/format'

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const detailVisible = ref(false)
const currentUser = ref<any>(null)
const query = reactive({ page: 1, page_size: 10, status: 1 as any, keyword: '' })
const verifyStatusText = (status: number) => ({ 0: '未提交', 1: '待审核', 2: '已通过', 3: '已驳回' } as Record<number, string>)[status] || '未知'
const verifyTagType = (status: number) => ({ 1: 'warning', 2: 'success', 3: 'danger' } as Record<number, any>)[status] || 'info'
const maskIdCard = (value?: string) => value && value.length >= 8 ? `${value.slice(0, 4)}**********${value.slice(-4)}` : '-'

const loadList = async () => { loading.value = true; try { const res = await adminApi.getIdentityReviews(query); list.value = res.data.list || []; total.value = res.data.total || 0 } finally { loading.value = false } }
const search = () => { query.page = 1; loadList() }
const openDetail = (row: any) => { currentUser.value = row; detailVisible.value = true }

const approveIdentity = async (row: any) => {
  await ElMessageBox.confirm(`确认“${row.real_name || row.nickname}”的实名资料准确无误吗？`, '审核确认', { confirmButtonText: '确认通过', cancelButtonText: '取消', type: 'success' })
  await adminApi.reviewUserIdentity(row.id, 'approve')
  ElMessage.success('实名认证已通过')
  detailVisible.value = false
  loadList()
}

const rejectIdentity = async (row: any) => {
  const { value } = await ElMessageBox.prompt('请说明资料存在的问题，用户可根据原因重新提交。', '驳回实名认证', { confirmButtonText: '确认驳回', cancelButtonText: '取消', inputType: 'textarea', inputPattern: /\S+/, inputErrorMessage: '请填写驳回原因' })
  await adminApi.reviewUserIdentity(row.id, 'reject', value)
  ElMessage.success('实名认证已驳回')
  detailVisible.value = false
  loadList()
}
onMounted(loadList)
</script>

<style scoped>
.review-page { padding: 20px; border: 1px solid #dfe7f0; border-radius: 8px; background: #fff; color: #172033; }
.page-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 20px; margin-bottom: 20px; }
.page-head h2 { margin: 0; font-size: 20px; }.page-head p { margin: 6px 0 0; color: #718096; font-size: 13px; }
.head-count { display: flex; align-items: baseline; gap: 5px; color: #718096; font-size: 12px; }.head-count strong { color: #1d4f91; font-size: 24px; font-variant-numeric: tabular-nums; }
.toolbar { display: grid; grid-template-columns: minmax(260px, 400px) 150px auto auto; gap: 10px; margin-bottom: 16px; padding: 14px; border-radius: 7px; background: #f6f8fb; }
.user-cell, .identity-user { display: flex; align-items: center; gap: 11px; min-width: 0; }.user-cell strong, .user-cell span { display: block; }.user-cell span { margin-top: 4px; color: #718096; font-size: 12px; }
.id-card { font-family: Consolas, 'Courier New', monospace; font-variant-numeric: tabular-nums; }.reject-reason { color: #c2413b; }.data-table { margin-bottom: 12px; }
.table-footer { display: flex; align-items: center; justify-content: space-between; color: #718096; font-size: 13px; }
.identity-detail { display: grid; gap: 18px; }.identity-user { padding-bottom: 16px; border-bottom: 1px solid #e8edf3; }.identity-user h3, .identity-user p { margin: 0; }.identity-user p { margin-top: 5px; color: #718096; font-size: 12px; }.identity-user .el-tag { margin-left: auto; }
.identity-detail dl { display: grid; margin: 0; border: 1px solid #e5eaf0; border-radius: 7px; }.identity-detail dl div { display: grid; grid-template-columns: 110px 1fr; padding: 13px 15px; }.identity-detail dl div + div { border-top: 1px solid #e5eaf0; }.identity-detail dt { color: #718096; }.identity-detail dd { margin: 0; color: #172033; }
.reason { padding: 13px; border: 1px solid #f2c7c4; border-radius: 7px; background: #fff7f6; color: #a33c37; }.reason p { margin: 5px 0 0; }.privacy-note { margin: 0; color: #8a96a8; font-size: 12px; }
@media (max-width: 760px) { .review-page { padding: 14px; }.page-head { flex-direction: column; }.toolbar { grid-template-columns: 1fr; } }
</style>
