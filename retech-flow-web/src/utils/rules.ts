import type { FormItemRule } from 'element-plus'

export const emailRules: FormItemRule[] = [
  { required: true, message: '请输入邮箱地址', trigger: 'blur' },
  { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
]

export const passwordRules: FormItemRule[] = [
  { required: true, message: '请输入密码', trigger: 'blur' },
  {
    validator: (_rule: any, value: string, callback: any) => {
      const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[_\.@])[a-zA-Z\d_\.@]{6,20}$/
      if (!pattern.test(value)) {
        callback(new Error('密码长度为 6-20 位，需包含大小写字母、数字及特殊字符（_ . @）'))
      } else {
        callback()
      }
    },
    trigger: 'blur'
  }
]

export const authCodeRules: FormItemRule[] = [
  { required: true, message: '请输入验证码', trigger: 'blur' },
  { len: 6, message: '验证码长度为6位', trigger: 'blur' },
]