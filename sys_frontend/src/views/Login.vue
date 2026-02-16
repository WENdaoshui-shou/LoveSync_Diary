<template>
  <div class="login-container">
    <el-card class="login-card">
      <div slot="header" class="login-header">
        <h2>LoveSync 后台管理系统</h2>
      </div>
      <el-form ref="loginForm" :model="loginForm" :rules="loginRules" label-width="0">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" prefix-icon="el-icon-user" placeholder="请输入用户名" clearable></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" prefix-icon="el-icon-lock" type="password" placeholder="请输入密码"
            clearable show-password @keyup.enter.native="handleLogin"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width: 100%" @click="handleLogin">
            登录
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
      loading: false
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
          this.$message.success('登录成功')

          try {
            await this.$router.push('/')
          } catch (err) {
            if (err.name === 'NavigationDuplicated') {
              this.$message.error('导航重复，忽略错误')
            } else {
              this.$message.error('跳转失败')
            }
          }
        } else {
          this.$message.error('登录失败：未获取到token')
        }
      } catch (error) {
        this.$message.error('登录失败，请检查用户名和密码')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;

  h2 {
    margin: 0;
    color: #303133;
    font-weight: 400;
  }
}
</style>