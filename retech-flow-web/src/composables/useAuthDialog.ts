import { ref } from 'vue'

export type AuthDialogMode = 'login' | 'register' | 'reset'

const visible = ref(false)
const mode = ref<AuthDialogMode>('login')

export const openAuthDialog = (nextMode: AuthDialogMode = 'login') => {
  mode.value = nextMode
  visible.value = true
}

export const closeAuthDialog = () => {
  visible.value = false
}

export const useAuthDialog = () => ({
  visible,
  mode,
  openAuthDialog,
  closeAuthDialog,
})
