<template>
  <DecorativeBackground>
    <div class="login-page">
      <div class="login-box">
        <div class="login-left">
          <div class="brand-info">
            <div class="brand-logo">
              <el-image class="brand-logo-img" :src="logo" fit="contain" alt="Logo" />
            </div>
            <div class="brand-slogan-container">
              <h2 class="brand-slogan">
                <span>拍照</span> · <span>描述</span> · <span>成交</span>
              </h2>
              <div class="slogan-decoration"></div>
            </div>
            <p class="brand-desc">
              <span class="ai-tag">AI</span> 全程代劳，成为您的私人质检师和定价师
            </p>
          </div>
          <el-icon class="decoration-icon icon-monitor"><Monitor /></el-icon>
          <el-icon class="decoration-icon icon-camera"><Camera /></el-icon>
          <el-icon class="decoration-icon icon-phone"><Iphone /></el-icon>
        </div>

        <!-- 表单区域 -->
        <div class="login-right">
          <!-- 表单插槽 -->
          <slot></slot>
        </div>
      </div>
    </div>
  </DecorativeBackground>
</template>

<script lang="ts" setup>
import { Monitor, Camera, Iphone } from "@element-plus/icons-vue";
import logo from '@/assets/icon.png'; 
import DecorativeBackground from '@/components/DecorativeBackground.vue';

</script>

<style scoped>
/* ⚠️ 把你刚才 Login.vue 里的布局相关 CSS 挪过来 */
.login-page { width: 100%; flex: 1; min-height: 100vh; display: flex; justify-content: center; align-items: center; background-color: transparent; }
.login-box { width: 888px; height: 550px; display: flex; border-radius: 24px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15); background: #ffffff; overflow: hidden; position: relative; }
.login-left { width: 400px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 60px 40px; display: flex; flex-direction: column; justify-content: center; position: relative; overflow: hidden; }
.brand-info { position: relative; z-index: 2; }
.brand-logo { margin-bottom: 70px; }
.brand-logo-img { width: 366px; height: 50px; }
.brand-slogan-container { margin-bottom: 30px; }
.brand-slogan { font-size: 36px; line-height: 1.3; font-weight: 800; letter-spacing: 1px; color: #ffffff; }
.slogan-decoration { width: 40px; height: 6px; background-color: #ffffff; border-radius: 3px; margin-top: 20px; opacity: 0.8; }
.brand-desc { font-size: 18px; line-height: 1.6; opacity: 0.9; font-weight: 400; display: flex; align-items: center; }
.ai-tag { background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(4px); border: 1px solid rgba(255, 255, 255, 0.4); padding: 2px 8px; border-radius: 6px; font-weight: 1000; margin-right: 10px; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.decoration-icon { position: absolute; color: rgba(255, 255, 255, 0.1); pointer-events: none; z-index: 1; }
.icon-monitor { font-size: 200px; top: -40px; right: -60px; transform: rotate(15deg); }
.icon-camera { font-size: 120px; bottom: 80px; left: -30px; transform: rotate(-20deg); }
.icon-phone { font-size: 100px; bottom: -20px; right: 20px; transform: rotate(30deg); }
.login-right { flex: 1; display: flex; align-items: center; justify-content: center; padding: 58px; background-color: #ffffff; }
</style>