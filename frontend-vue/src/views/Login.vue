<template>
  <div class="login-container">
    <!-- 左侧绿色背景 -->
    <div class="login-left-panel">
      <div class="left-content">
        <div class="logo-section">
          <div class="logo-text">Schneider Electric</div>
          <div class="logo-subtext">订单查询系统</div>
        </div>
        <div class="welcome-section">
          <div class="welcome-title">欢迎使用<br>施耐德订单查询系统!</div>
          <div class="welcome-desc">
            一键登录,畅享便捷。在这里,您可随时查询订单状态,获取专属业务支持与服务。专属订单管家,为您提供一站式智慧服务!
          </div>
        </div>
        <div class="dots">
          <span class="dot active"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="login-right-panel">
      <div class="login-form-container">
        <h2 class="form-title">登录账户</h2>
        <p class="form-subtitle">输入您的凭据以访问系统</p>

        <el-form :model="loginForm" :rules="rules" ref="formRef" class="login-form">
          <el-form-item prop="username">
            <el-input 
              v-model="loginForm.username" 
              placeholder="请输入用户名"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="请输入密码"
              :prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <a href="#" class="forgot-link">忘记密码?</a>
          </div>

          <el-button 
            type="primary" 
            size="large" 
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form>

        <div class="register-link">
          还没有账户? <a href="#">立即注册</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await login(loginForm.username, loginForm.password)

        if (response.success) {
          // 使用 Pinia store 管理用户状态
          userStore.setUser({
            token: response.access_token || response.token,
            user_id: response.user_id,
            username: response.username || loginForm.username
          })
          ElMessage.success(response.message || '登录成功')
          router.push('/query')
        } else {
          ElMessage.error(response.message || '登录失败')
        }
      } catch (error) {
        if (error.code === 'ECONNREFUSED') {
          ElMessage.error('无法连接到后端服务,请确保 FastAPI 服务已启动')
        } else {
          ElMessage.error(error.message || '登录异常')
        }
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  min-height: 100vh;
}

.login-left-panel {
  width: 50%;
  background: linear-gradient(135deg, #3DCD58 0%, #2BA845 100%);
  padding: 80px 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login-left-panel::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 600px;
  height: 600px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
  animation: float 20s ease-in-out infinite;
}

.login-left-panel::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: -15%;
  width: 500px;
  height: 500px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 50%;
  animation: float 15s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(30px, -30px) rotate(120deg); }
  66% { transform: translate(-20px, 20px) rotate(240deg); }
}

.left-content {
  position: relative;
  z-index: 10;
}

.logo-section {
  margin-bottom: 60px;
}

.logo-text {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin-bottom: 5px;
}

.logo-subtext {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.welcome-section {
  animation: fadeInUp 1s ease-out 0.2s both;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

.welcome-title {
  font-size: 42px;
  font-weight: 700;
  color: white;
  line-height: 1.3;
  margin-bottom: 30px;
}

.welcome-desc {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.8;
  max-width: 520px;
}

.dots {
  display: flex;
  gap: 12px;
  margin-top: 50px;
}

.dot {
  width: 10px;
  height: 10px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 50%;
}

.dot.active {
  width: 30px;
  background: white;
  border-radius: 5px;
}

.login-right-panel {
  width: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.login-form-container {
  width: 380px;
  padding: 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
}

.form-title {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.form-subtitle {
  font-size: 14px;
  color: #666;
  margin-bottom: 30px;
}

.login-form {
  margin-top: 20px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 15px 0 25px;
}

.forgot-link {
  color: #3DCD58;
  text-decoration: none;
  font-size: 14px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #3DCD58 0%, #2BA845 100%);
  border: none;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(61, 205, 88, 0.4);
}

.register-link {
  text-align: center;
  margin-top: 25px;
  font-size: 13px;
  color: #999;
}

.register-link a {
  color: #3DCD58;
  text-decoration: none;
}

@media (max-width: 900px) {
  .login-left-panel {
    display: none;
  }
  
  .login-right-panel {
    width: 100%;
  }
}
</style>
