import { defineStore } from 'pinia'
import { ref } from 'vue'
import goodsApi, { type CategoryData } from '@/api/goodsapi'

export const useCategoryStore = defineStore('category', () => {
  // 分类数据字典
  const categories = ref<CategoryData[]>([])

  const fetchCategories = async () => {
    try {
      const res = await goodsApi.getCategoriesAPI()
      if (res.code === 200 && res.data) {
        categories.value = res.data
      }
    } catch (e) {
      console.error('Failed to fetch categories:', e)
    }
  }

  // 发货方式字典 (必须与后端 models.py DeliveryMethodChoices 保持一致)
  const shippingMethods = ref([
    { id: 1, name: '包邮' },
    { id: 2, name: '到付' },
    { id: 3, name: '自提' }
  ])

  return {
    categories,
    shippingMethods,
    fetchCategories
  }
})
