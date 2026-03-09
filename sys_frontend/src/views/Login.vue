<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
      <div class="bg-circle bg-circle-3"></div>
    </div>

    <el-card class="login-card animate-fade-in">
      <div slot="header" class="login-header animate-slide-in" style="animation-delay: 0.2s;">
        <div class="logo-container">
          <div class="logo-icon">
            <span class="logo-heart">❤</span>
          </div>
          <h2>LoveSync 后台管理系统</h2>
        </div>
        <p class="login-subtitle">欢迎回来，管理员</p>
      </div>

      <!-- 成功动画 -->
      <div v-if="showSuccessAnimation" class="success-animation">
        <div class="success-icon">✓</div>
        <div class="success-text">登录成功</div>
        <div class="success-subtext">正在跳转...</div>
      </div>

      <el-form v-else ref="loginForm" :model="loginForm" :rules="loginRules" label-width="0">
        <el-form-item prop="username" class="animate-slide-in form-item" style="animation-delay: 0.4s;">
          <el-input v-model="loginForm.username" prefix-icon="el-icon-user" placeholder="请输入用户名" clearable
            class="form-input" @focus="onInputFocus('username')" @blur="onInputBlur('username')"></el-input>
        </el-form-item>
        <el-form-item prop="password" class="animate-slide-in form-item" style="animation-delay: 0.6s;">
          <el-input v-model="loginForm.password" prefix-icon="el-icon-lock" type="password" placeholder="请输入密码"
            clearable show-password @keyup.enter.native="handleLogin" class="form-input"
            @focus="onInputFocus('password')" @blur="onInputBlur('password')"></el-input>
        </el-form-item>
        <el-form-item class="animate-slide-in" style="animation-delay: 0.8s;">
          <el-button type="primary" :loading="loading" class="login-button" @click="handleLogin"
            :class="{ 'button-active': isButtonActive }" @mousedown="isButtonActive = true"
            @mouseup="isButtonActive = false" @mouseleave="isButtonActive = false">
            <span v-if="!loading">登录</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { login } from '@/api/auth'

export default {
  name: 'AdminLogin',
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      },
      loading: false,
      isButtonActive: false,
      focusedInput: '',
      showSuccessAnimation: false
    }
  },
  created() {
    // 检查是否已经登录，如果已登录则跳转到首页
    const token = localStorage.getItem('admin_token')
    if (token) {
      this.$router.replace('/')
    }
  },
  methods: {
    async handleLogin() {
      try {
        const valid = await this.$refs.loginForm.validate()
        if (!valid) {
          return
        }

        this.loading = true

        const response = await login(this.loginForm)

        const token = response.data.access
        if (token) {
          localStorage.setItem('admin_token', token)

          // 显示成功动画
          this.showSuccessAnimation = true

          // 等待动画完成后跳转到首页
          setTimeout(async () => {
            try {
              await this.$router.push('/')
            } catch (err) {
              if (err.name === 'NavigationDuplicated') {
                this.$message.error('导航重复，忽略错误')
              } else {
                this.$message.error('跳转失败')
              }
            }
          }, 1500)
        } else {
          this.$message.error('登录失败：未获取到token')
        }
      } catch (error) {
        this.$message.error('登录失败，请检查用户名和密码')
      } finally {
        this.loading = false
      }
    },

    onInputFocus(input) {
      this.focusedInput = input
    },

    onInputBlur() {
      this.focusedInput = ''
    }
  }
}
</script>

<style lang="scss" scoped>
/* 导入Inter字体 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #FF6B8B 0%, #722ED1 100%);
  position: relative;
  overflow: hidden;
  font-family: 'Inter', sans-serif;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(50px);
  animation: float 8s ease-in-out infinite;
}

.bg-circle-1 {
  top: -10%;
  left: -10%;
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.1);
}

.bg-circle-2 {
  bottom: -10%;
  right: -10%;
  width: 400px;
  height: 400px;
  background: rgba(255, 255, 255, 0.15);
  animation-delay: -2s;
}

.bg-circle-3 {
  top: 50%;
  right: 20%;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  animation-delay: -4s;
}

@keyframes float {

  0%,
  100% {
    transform: translateY(0) translateX(0);
  }

  33% {
    transform: translateY(-20px) translateX(10px);
  }

  66% {
    transform: translateY(10px) translateX(-20px);
  }
}

.login-card {
  width: 420px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  z-index: 1;
}

.login-card:hover {
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  transform: translateY(-5px);
}

.login-header {
  text-align: center;
  padding: 24px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(255, 107, 139, 0.3);
  background: linear-gradient(135deg, #FF6B8B 0%, #722ED1 100%);
  border-radius: 50%;
  transition: all 0.3s ease;
}

.logo-heart {
  font-size: 20px;
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.login-header h2 {
  margin: 0;
  color: #303133;
  font-weight: 600;
  font-size: 24px;
  letter-spacing: -0.025em;
}

.login-subtitle {
  margin: 8px 0 0 0;
  color: #909399;
  font-size: 14px;
  font-weight: 400;
}

/* 表单样式 */
.el-form {
  padding: 0 32px 32px;
}

.form-item {
  margin-bottom: 20px;
}

.form-input {
  border-radius: 8px;
  transition: all 0.3s ease;
  height: 48px;
  font-size: 14px;
}

/* 针对 Element Plus 输入框的样式调整 */
:deep(.el-input__wrapper) {
  border-radius: 8px !important;
  height: 48px !important;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 2px rgba(255, 107, 139, 0.1) !important;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(255, 107, 139, 0.2) !important;
  border-color: #FF6B8B !important;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  height: 48px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #FF6B8B 0%, #722ED1 100%);
  border: none;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 139, 0.4);
}

.login-button.button-active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(255, 107, 139, 0.3);
}

.login-button::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transform: rotate(45deg);
  animation: shine 3s infinite;
}

@keyframes shine {
  0% {
    transform: translateX(-100%) rotate(45deg);
  }

  100% {
    transform: translateX(100%) rotate(45deg);
  }
}

/* 动画效果 */
.animate-fade-in {
  animation: fadeIn 0.8s ease-out forwards;
  opacity: 0;
  transform: translateY(30px);
}

.animate-slide-in {
  animation: slideIn 0.6s ease-out forwards;
  opacity: 0;
  transform: translateY(20px);
}

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 成功动画样式 */
.success-animation {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: white;
  margin-bottom: 20px;
  animation: successPop 0.6s ease-out forwards, successPulse 2s ease-in-out infinite;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.success-text {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  animation: successFadeIn 0.6s ease-out 0.2s forwards;
  opacity: 0;
  transform: translateY(20px);
}

.success-subtext {
  font-size: 14px;
  color: #909399;
  animation: successFadeIn 0.6s ease-out 0.4s forwards;
  opacity: 0;
  transform: translateY(20px);
}

@keyframes successPop {
  0% {
    transform: scale(0);
    opacity: 0;
  }

  50% {
    transform: scale(1.2);
    opacity: 1;
  }

  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes successPulse {

  0%,
  100% {
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
  }

  50% {
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.5);
  }
}

@keyframes successFadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    width: 90%;
    max-width: 360px;
  }

  .el-form {
    padding: 0 24px 24px;
  }

  .login-header h2 {
    font-size: 20px;
  }

  .success-icon {
    width: 60px;
    height: 60px;
    font-size: 30px;
  }

  .success-text {
    font-size: 20px;
  }
}
</style>