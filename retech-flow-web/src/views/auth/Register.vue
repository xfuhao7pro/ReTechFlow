<template>
  <AuthLayout>
    <div class="form-wrapper">
      <h2 class="welcome-text">创建账号</h2>
      <p class="welcome-sub">填写以下信息完成注册</p>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="login-form"
        size="large"
      >
        <!-- 邮箱输入框 -->
        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱地址"
            :prefix-icon="Message"
          />
        </el-form-item>
        <!-- 密码输入框 -->
        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <!-- 确认密码 -->
        <el-form-item prop="password_confirm">
          <el-input
            v-model="registerForm.password_confirm"
            type="password"
            placeholder="请再次输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <!-- 验证码输入框-->
        <el-form-item prop="auth_code">
          <el-input
            v-model="registerForm.auth_code"
            placeholder="请输入验证码"
            :prefix-icon="Key"
          >
            <template #suffix>
              <el-button 
                link
                type="primary"
                class="suffix-code-btn"
                :disabled="isSendingCode || countdown > 0"
                @click="handleSendCode"
              >
                {{ countdown > 0 ? `${countdown}s 后重试` : '获取验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>

        <!-- 注册按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            class="login-btn"
            :loading="loading"
            @click="handleRegister"
          >
            立即注册
          </el-button>
        </el-form-item>

        <!-- 登录引导 -->
        <div class="register-guide">
          已有账号？
          <el-link type="primary" :underline="false" @click="router.push('/login')">
            立即登录
          </el-link>
        </div>
      </el-form>
    </div>
  </AuthLayout>
</template>

<script lang="ts" setup name="register">
import AuthLayout from "@/components/AuthLayout.vue";
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { Message, Lock, Key } from "@element-plus/icons-vue";
import type { FormInstance, FormRules } from "element-plus";
import { ElMessage } from "element-plus";
import authAPI from "@/api/authapi";
import {emailRules,passwordRules,authCodeRules} from "@/utils/rules"
import { useVcode } from '@/composables/useVcode'

const router = useRouter();
const registerFormRef = ref<FormInstance>();
const { verify } = useVcode()
const loading = ref(false);
// 验证码按钮状态
const isSendingCode = ref(false);
const countdown = ref(0);
let timer: ReturnType<typeof setInterval> | null = null;

const registerForm = reactive({
  email: "",
  auth_code: "",
  password: "",
  password_confirm: "",
});
// 密码校验
const validatePass2 = (_rule: any, value: string, callback: any) => {
  if (value === "") {
    callback(new Error("请再次输入密码"));
  } else if (value !== registerForm.password) {
    callback(new Error("两次输入密码不一致!"));
  } else {
    callback();
  }
};
// 注册表单规则
const registerRules = reactive<FormRules>({
  email: emailRules,
  password: passwordRules,
  auth_code: authCodeRules,
  password_confirm: [
    { required: true, validator: validatePass2, trigger: "blur" },
  ],
});

// 发验证码接口
const handleSendCode = async () => {
  // validateField 已经包含了非空和格式校验，不需要再单独判断
  try {
    await registerFormRef.value?.validateField('email')
  } catch {
    return
  }

  // 触发全局滑块验证
  const isVerified = await verify()
  if (!isVerified) {
    ElMessage.warning('验证未通过，无法发送验证码')
    return
  }

  isSendingCode.value = true
  try {
    const res = await authAPI.sendCodeAPI(registerForm.email)
    if (res.code === 200) {
      ElMessage.success('验证码已发送，请查收')
      startCountdown()
    }
  } catch (error) {
    console.error(error)
  } finally {
    isSendingCode.value = false
  }
}


// 倒计时逻辑
const startCountdown = () => {
  countdown.value = 60;
  if (timer) clearInterval(timer);
  timer = setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) {
      if (timer) clearInterval(timer);
    }
  }, 1000);
};

// 注册逻辑
const handleRegister = async () => {
  if (!registerFormRef.value) return;
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const res = await authAPI.registerAPI({
          email: registerForm.email,
          auth_code: registerForm.auth_code,
          password: registerForm.password,
          password_confirm: registerForm.password_confirm
        });
        
        if (res.code === 200) {
          ElMessage.success("注册成功，请登录！");
          router.push("/login");
        } else {
          ElMessage.error(res.msg || "注册失败");
        }
      } catch (error) {
        console.error(error);
        ElMessage.error("注册服务异常");
      } finally {
        loading.value = false;
      }
    }
  });
};

</script>

<style scoped>
.form-wrapper {
  width: 100%;
  max-width: 380px;
}

.welcome-text {
  font-size: 28px;
  color: #1e293b;
  margin-bottom: 8px;
  font-weight: 700;
  margin-top: 60px;
}

.welcome-sub {
  font-size: 15px;
  color: #64748b;
  margin-bottom: 10px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 30px; 
}

.login-form :deep(.el-input__wrapper) {
  background-color: #f8fafc;
  box-shadow: none;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  padding: 10px 15px;
  border-radius: 10px;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  background-color: #fff;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.login-form :deep(.el-input__inner) {
  height: 44px;
  font-size: 15px;
}

/* 验证码后缀按钮样式 */
.suffix-code-btn {
  font-weight: 600;
  padding: 4px 10px;
  height: auto;
  border: 1px solid transparent; 
  border-radius: 4px;
  transition: all 0.3s;
}

.suffix-code-btn:not(.is-disabled):hover {
  background-color: #ecf5ff;
  border-color: #b3d8ff;
}

.login-btn {
  width: 100%;
  height: 52px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
  transition: all 0.2s ease;
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
}

.login-btn:active {
  transform: translateY(0);
}

.register-guide {
  text-align: center;
  margin-top: 24px;
  color: #64748b;
  font-size: 14px;
}

.register-guide .el-link {
  vertical-align: baseline;
  margin-left: 5px;
  font-weight: 600;
  font-size: 14px;
}
</style>
