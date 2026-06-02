import { ref } from 'vue'

// 使用单例模式保存状态
const isShow = ref(false)
let resolvePromise: ((value: boolean) => void) | null = null

export function useVcode() {
  /**
   * 触发验证，返回一个 Promise，验证成功为 true，关闭或失败不返回 true
   */
  const verify = (): Promise<boolean> => {
    isShow.value = true
    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  /**
   * 内部方法，供 App.vue 中的全局组件调用
   */
  const handleSuccess = () => {
    isShow.value = false
    if (resolvePromise) {
      resolvePromise(true)
      resolvePromise = null
    }
  }

  const handleClose = () => {
    isShow.value = false
    if (resolvePromise) {
      resolvePromise(false)
      resolvePromise = null
    }
  }

  return {
    isShow,
    verify,
    handleSuccess,
    handleClose
  }
}
