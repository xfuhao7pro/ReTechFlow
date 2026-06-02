<template>
  <DecorativeBackground>
    <div class="orders-placeholder">
      <el-empty :description="description" />
    </div>
  </DecorativeBackground>
</template>

<script lang="ts" setup name="OrdersContentPlaceholder">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DecorativeBackground from '@/components/DecorativeBackground.vue'

const route = useRoute()

const description = computed(() => {
  const title = route.meta?.title
  return typeof title === 'string' ? `${title} · 内容开发中` : '内容开发中'
})
</script>

<style scoped>
.orders-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
