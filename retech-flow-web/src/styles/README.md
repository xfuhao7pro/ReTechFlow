# 装饰背景样式使用说明

## decorative-background.css

这是一个可复用的装饰背景样式文件，提供白色为主的背景，配合不规则的炫彩喷墨和线条装饰效果。

### 使用方法

#### 1. 在 Vue 组件中引入样式

在 `<style scoped>` 标签中导入样式文件：

```vue
<style scoped>
@import '@/styles/decorative-background.css';
</style>
```

#### 2. 在模板中添加类名和装饰元素

在你的根容器元素上添加 `decorative-bg` 类，并添加装饰元素：

```vue
<template>
  <div class="your-page decorative-bg">
    <!-- 装饰元素 -->
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
    
    <!-- 你的页面内容 -->
    <div class="content">
      ...
    </div>
  </div>
</template>
```

#### 3. 确保内容层级正确

装饰背景样式会自动将所有直接子元素的 `z-index` 设置为 1，确保内容显示在装饰元素之上。

### 装饰元素说明

- **ink-splash-1, ink-splash-2**: 不规则的喷墨效果，使用多种颜色
- **line-decoration-1~4**: 不规则的线条装饰，不同角度和颜色
- **curve-line-1, curve-line-2**: 曲线装饰，增加动感
- **dot-pattern-1, dot-pattern-2**: 点阵图案，增加细节

### 适用页面

- 我发布的 (MyPublished.vue) ✓ 已应用
- 我买到的 (待创建)
- 我卖出的 (待创建)
- 我的收藏 (MyLikes.vue) - 可选应用
- 其他订单相关页面

### 自定义

如果需要调整装饰元素的位置、颜色或大小，可以在组件的 `<style scoped>` 中覆盖相应的类样式。

例如：

```vue
<style scoped>
@import '@/styles/decorative-background.css';

.ink-splash-1 {
  top: 20%;
  left: -3%;
}
</style>
```
