<template>
  <div class="decorative-bg">
    <div class="ink-splash-1"></div>
    <div class="ink-splash-2"></div>
    <div class="line-decoration-1"></div>
    <div class="line-decoration-2"></div>
    <div class="line-decoration-3"></div>
    <div class="line-decoration-4"></div>
    <div class="curve-line-1"></div>
    <div class="curve-line-2"></div>
    <div class="dot-pattern-1"></div>
    <div class="dot-pattern-2"></div>
    
    <!-- 所有的子内容都会被放到这里，并保持 z-index 层级 -->
    <div class="content-wrapper">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
// 这是一个纯展示的背景包裹组件，没有额外的逻辑
</script>

<style scoped>
@import '@/styles/decorative-background.css';

.decorative-bg {
  width: 100%;
  height: 100%;
  min-height: 0;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  position: relative;
  z-index: 1;
  width: 100%;
  flex: 1;
  min-height: 0;
  /* grid 1fr 强制子元素撑满容器 */
  display: grid;
  grid-template-rows: 1fr;
  grid-template-columns: 1fr;
  overflow-y: auto;
  overflow-x: hidden;
  /* 完全隐藏滚动条，不占任何空间，杜绝切换组件时的占位抖动 */
  scrollbar-width: none;            /* Firefox */
  -ms-overflow-style: none;         /* IE / Edge */
}

.content-wrapper::-webkit-scrollbar {
  display: none;                    /* Chromium / Safari */
}
</style>
