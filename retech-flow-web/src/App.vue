<template>
  <router-view></router-view>
  <!-- 全局单例滑块验证组件 -->
  <Vcode 
    :show="isShow" 
    @success="handleSuccess" 
    @close="handleClose" 
  />
</template>

<script setup lang="ts">
import Vcode from 'vue3-puzzle-vcode'
import { useVcode } from '@/composables/useVcode'

const { isShow, handleSuccess, handleClose } = useVcode()
</script>

<style>
body {
  margin: 0;
  padding: 0;
}
</style>