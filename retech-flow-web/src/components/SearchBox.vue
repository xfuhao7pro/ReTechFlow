<template>
  <div class="search-box">
    <input
      class="search-box__input"
      :value="modelValue"
      :placeholder="placeholder"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      @keyup.enter="$emit('search')"
    />
    <button class="search-box__btn" @click="$emit('search')">
      <el-icon :size="16"><Search /></el-icon>
      <span>搜索</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { Search } from '@element-plus/icons-vue'

defineProps<{
  modelValue: string
  placeholder?: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
  'search': []
}>()
</script>

<style scoped lang="scss">
.search-box {
  display: inline-flex;
  align-items: stretch;
  width: 100%;
  height: 40px;
  box-sizing: border-box;
  border: 2px solid #1a1a1a;
  border-radius: 24px;
  overflow: hidden;
  background: #fff;
  transition: border-color 0.25s, box-shadow 0.25s;

  &:focus-within {
    border-color: #409eff;
    box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.15);
  }
}

.search-box__input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  padding: 0 16px;
  font-size: 14px;
  color: #333;
  background: transparent;

  &::placeholder {
    color: #bbb;
  }
}

.search-box__btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 20px;
  border: none;
  background: #409eff;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;

  &:hover {
    background: #66b1ff;
  }

  &:active {
    background: #3a8ee6;
  }
}
</style>
