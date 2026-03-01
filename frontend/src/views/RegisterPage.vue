<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { AppRoutes } from '@/constants/appRoutes'
import { Loading } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const username = ref('')
const password = ref('')
const confirmPassword = ref('')

async function handleRegister() {
  if (password.value !== confirmPassword.value) {
    ElMessage.error('Passwords do not match')
    return
  }

  const result = await authStore.register(email.value, password.value, username.value)

  if (result.success) {
    ElMessage.success('Registration successful! Please login.')
    router.push(AppRoutes.LOGIN)
  }
}
</script>

<template>
  <div class="register-page">
    <el-card v-if="!authStore.isCheckingAuth" class="register-card">
      <template #header>
        <h2>Register</h2>
      </template>
      <el-form @submit.prevent="handleRegister">
        <el-form-item label="Email">
          <el-input
            v-model="email"
            type="email"
            placeholder="Enter your email"
            :disabled="authStore.isLoading"
          />
        </el-form-item>
        <el-form-item label="Username">
          <el-input
            v-model="username"
            placeholder="Enter your username"
            :disabled="authStore.isLoading"
          />
        </el-form-item>
        <el-form-item label="Password">
          <el-input
            v-model="password"
            type="password"
            placeholder="Enter your password"
            show-password
            :disabled="authStore.isLoading"
          />
        </el-form-item>
        <el-form-item label="Confirm Password">
          <el-input
            v-model="confirmPassword"
            type="password"
            placeholder="Confirm your password"
            show-password
            :disabled="authStore.isLoading"
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="authStore.isLoading"
            @click="handleRegister"
            style="width: 100%"
          >
            Register
          </el-button>
        </el-form-item>
        <div>
          <el-link type="primary" @click="$router.push('/login')">
            Already have an account? Login
          </el-link>
        </div>
      </el-form>
      <el-alert
        v-if="authStore.error && !authStore.error.includes('auth') && !authStore.error.includes('authorized')"
        :title="authStore.error"
        type="error"
        :closable="false"
        style="margin-top: 20px"
      />
    </el-card>
    <el-card v-else class="register-card">
      <div style="text-align: center; padding: 40px;">
        <el-icon class="is-loading" style="font-size: 32px;">
          <Loading />
        </el-icon>
        <p style="margin-top: 16px;">Checking authentication...</p>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 400px;
}

:deep(.el-input__inner) {
  -webkit-text-fill-color: inherit !important;
  transition: background-color 5000s ease-in-out 0s;
}

:deep(.el-input__inner:-webkit-autofill) {
  -webkit-box-shadow: 0 0 0 1000px white inset !important;
  -webkit-text-fill-color: inherit !important;
}

:deep(.dark .el-input__inner:-webkit-autofill) {
  -webkit-box-shadow: 0 0 0 1000px rgb(31 41 55) inset !important;
  -webkit-text-fill-color: inherit !important;
}
</style>

