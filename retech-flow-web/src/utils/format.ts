import { runtimeConfig } from '@/config/runtime'

const normalizeLegacyAvatarPath = (path: string): string => {
  const match = path.match(/^(?:\/?media\/)?(?:\/?avatars\/)?default_(0[1-5])\.png$/)
  return match ? `avatars/default_avatar_${match[1]}.png` : path
}

/**
 * 全局格式化工具函数
 */

/**
 * 格式化价格，保留两位小数或显示整数
 */
export const formatPrice = (price: number | string): string => {
  const num = Number(price);
  if (isNaN(num)) return "0.00";
  return Number.isInteger(num) ? String(num) : num.toFixed(2);
};

/**
 * 格式化时间字符串
 */
export const formatTime = (dateStr: string | null | undefined): string => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  const h = String(date.getHours()).padStart(2, '0');
  const min = String(date.getMinutes()).padStart(2, '0');
  return `${y}-${m}-${d} ${h}:${min}`;
};

/**
 * 处理商品图片，将相对路径转为绝对路径（使用环境变量中的 baseURL）
 */
export const getImageUrl = (imagePath: string | null | undefined): string => {
  if (!imagePath) return '';
  imagePath = normalizeLegacyAvatarPath(imagePath)
  
  // 如果已经是完整URL，直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://') || imagePath.startsWith('blob:')) {
    return imagePath;
  }
  
  // 获取后端基础URL (去除末尾斜杠)
  const baseUrl = runtimeConfig.apiBaseUrl;
  
  // 确保以斜杠开头
  const normalizedPath = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;
  
  // 如果是以 /media/ 开头的路径，或者本身就不包含 media，则按需拼接
  if (normalizedPath.startsWith('/media/')) {
    return `${baseUrl}${normalizedPath}`;
  }
  
  // 特殊处理：如果是 avatars/ 开头的（比如后端传来的 avatars/default_01.png）
  return `${baseUrl}/media${normalizedPath}`;
};
