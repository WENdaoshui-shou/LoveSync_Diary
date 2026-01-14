<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2 class="login-title">LoveSync 情侣日记本</h2>
        <p class="login-subtitle">记录你们的美好时光</p>
      </div>

      <el-form ref="loginForm" :model="loginForm" :rules="rules" label-position="top" class="login-form">
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="el-icon-user"
            clearable
          ></el-input>
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="el-icon-lock"
            clearable
            show-password
          ></el-input>
        </el-form-item>

        <el-form-item>
          <div class="login-options">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <el-link type="primary" :underline="false" @click="$router.push('/register')">
              注册账号
            </el-link>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="login-btn"
            @click="handleLogin"
            :loading="loading"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p>其他登录方式</p>
        <div class="login-social">
          <el-button icon="el-icon-mobile" circle></el-button>
          <el-button icon="el-icon-chat-line-square" circle></el-button>
          <el-button icon="el-icon-document" circle></el-button>
        </div>
      </div>
    </div>

    <div class="login-bg">
      <div class="login-bg-content">
        <h3>欢迎回来</h3>
        <p>与你的伴侣一起记录美好时光</p>
        <div class="login-bg-features">
          <div class="feature-item">
            <i class="el-icon-date"></i>
            <span>记录生活点滴</span>
          </div>
          <div class="feature-item">
            <i class="el-icon-like"></i>
            <span>分享幸福瞬间</span>
          </div>
          <div class="feature-item">
            <i class="el-icon-video-camera"></i>
            <span>珍藏美好回忆</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data () {
    return {
      loginForm: {
        username: '',
        password: '',
        remember: false
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 6, max: 20, message: '用户名长度在 6 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
        ]
      },
      loading: false
    }
  },
  methods: {
    async handleLogin () {
      this.$refs.loginForm.validate(async (valid) => {
        if (valid) {
          this.loading = true
          try {
            await this.$store.dispatch('login', this.loginForm)
            const redirect = this.$route.query.redirect || '/index'
            this.$router.push(redirect)
            this.$message.success('登录成功')
          } catch (error) {
            this.$message.error(error.detail || '登录失败，请检查用户名和密码')
          } finally {
            this.loading = false
          }
        } else {
          this.$message.warning('请填写完整的登录信息')
          return false
        }
      })
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  min-height: 100vh;
  background-color: #f9f9f9;
}

.login-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-title {
  font-size: 28px;
  font-weight: bold;
  color: var(--primary-color);
  margin-bottom: 10px;
}

.login-subtitle {
  font-size: 16px;
  color: var(--text-color-secondary);
}

.login-form {
  width: 100%;
  max-width: 400px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.login-btn {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  background: linear-gradient(135deg, #FF6B8B 0%, #722ED1 100%);
  border: none;
}

.login-btn:hover {
  background: linear-gradient(135deg, #FF879E 0%, #8240D4 100%);
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  color: var(--text-color-secondary);
}

.login-social {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 15px;
}

.login-bg {
  flex: 1;
  background: linear-gradient(135deg, #FF6B8B 0%, #722ED1 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  padding: 40px;
}

.login-bg-content {
  max-width: 400px;
}

.login-bg-content h3 {
  font-size: 32px;
  margin-bottom: 20px;
}

.login-bg-content p {
  font-size: 18px;
  margin-bottom: 40px;
  opacity: 0.9;
}

.login-bg-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 16px;
}

.feature-item i {
  font-size: 24px;
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }

  .login-bg {
    display: none;
  }
}
</style>
