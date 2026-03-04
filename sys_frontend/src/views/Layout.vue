<template>
  <div class="admin-layout">
    <!-- 背景装饰元素 -->
    <div class="bg-decoration">
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
      <div class="bg-circle bg-circle-3"></div>
    </div>

    <el-container class="layout-container" style="height: 100vh; display: flex; flex-direction: column;">
      <!-- 头部 -->
      <el-header class="layout-header">
        <div class="header-content">
          <!-- 品牌标识 -->
          <div class="logo">
            <a href="/" class="logo-link">
              <div class="logo-icon">
                <span class="logo-heart">❤</span>
              </div>
              <div class="logo-text">
                <span class="logo-main">LoveSync</span>
              </div>
            </a>
          </div>

          <!-- 系统描述 -->
          <div class="header-description">
            <p class="description-text">一站式管理平台</p>
          </div>

          <!-- 用户信息 -->
          <div class="header-right">
            <div class="user-info" v-if="userInfo">
              <el-dropdown trigger="click" class="user-dropdown">
                <div class="user-avatar">
                  <img
                    :src="userInfo.avatar || 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=professional%20user%20avatar%20icon%20minimal%20design&image_size=square'"
                    :alt="userInfo.username" class="avatar-img" />
                  <span class="user-name">{{ userInfo.username }}</span>
                  <i class="el-icon-arrow-down user-arrow"></i>
                </div>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item @click="handleCommand('logout')">
                    <i class="el-icon-switch-button"></i>
                    <span>退出登录</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </el-dropdown>
            </div>
            <div class="user-info" v-else>
              <el-button type="primary" plain @click="handleCommand('login')">
                <i class="el-icon-user"></i>
                <span>登录</span>
              </el-button>
            </div>
          </div>
        </div>
      </el-header>

      <el-container style="flex: 1; display: flex; overflow: hidden;">
        <!-- 侧边栏 -->
        <el-aside width="300px" class="layout-aside" style="position: relative; flex-shrink: 0; overflow-y: auto;">
          <el-menu :default-active="$route.path" class="layout-menu" router background-color="rgba(255, 255, 255, 0.95)"
            text-color="#757575" active-text-color="#FF6B8B" :unique-opened="true" :collapse-transition="true">
            <el-menu-item index="/" class="menu-item">
              <i class="el-icon-s-home menu-icon"></i>
              <span slot="title">首页</span>
            </el-menu-item>

            <el-menu-item index="/users" class="menu-item">
              <i class="el-icon-user menu-icon"></i>
              <span slot="title">用户管理</span>
            </el-menu-item>

            <el-menu-item index="/moments" class="menu-item">
              <i class="el-icon-news menu-icon"></i>
              <span slot="title">动态管理</span>
            </el-menu-item>

            <el-submenu index="/community" class="menu-item">
              <template slot="title">
                <i class="el-icon-s-grid menu-icon"></i>
                <span>社区管理</span>
              </template>
              <el-menu-item index="/community/events" class="sub-menu-item">
                <i class="el-icon-date sub-menu-icon"></i>
                <span slot="title">社区活动</span>
              </el-menu-item>
              <el-menu-item index="/community/articles" class="sub-menu-item">
                <i class="el-icon-document sub-menu-icon"></i>
                <span slot="title">文章专栏管理</span>
              </el-menu-item>
              <el-menu-item index="/community/articles/list" class="sub-menu-item">
                <i class="el-icon-document sub-menu-icon"></i>
                <span slot="title">文章管理</span>
              </el-menu-item>
              <el-menu-item index="/community/topics" class="sub-menu-item">
                <i class="el-icon-top sub-menu-icon"></i>
                <span slot="title">热门话题</span>
              </el-menu-item>
              <el-menu-item index="/community/reports" class="sub-menu-item">
                <i class="el-icon-warning-outline sub-menu-icon"></i>
                <span slot="title">举报管理</span>
              </el-menu-item>
            </el-submenu>

            <el-submenu index="/couple" class="menu-item">
              <template slot="title">
                <i class="el-icon-connection menu-icon"></i>
                <span>情侣管理</span>
              </template>
              <el-menu-item index="/couple/recommended" class="sub-menu-item">
                <i class="el-icon-sunny sub-menu-icon"></i>
                <span slot="title">推荐情侣管理</span>
              </el-menu-item>
              <el-menu-item index="/couple/places" class="sub-menu-item">
                <i class="el-icon-s-flag sub-menu-icon"></i>
                <span slot="title">地点管理</span>
              </el-menu-item>
              <el-menu-item index="/couple/tests" class="sub-menu-item">
                <i class="el-icon-question sub-menu-icon"></i>
                <span slot="title">爱情测试管理</span>
              </el-menu-item>
              <el-menu-item index="/couple/games" class="sub-menu-item">
                <i class="el-icon-s-grid sub-menu-icon"></i>
                <span slot="title">情侣游戏管理</span>
              </el-menu-item>
            </el-submenu>

            <el-submenu index="/mall" class="menu-item">
              <template slot="title">
                <i class="el-icon-s-shop menu-icon"></i>
                <span>商城管理</span>
              </template>
              <!-- 商品管理 -->
              <el-menu-item index="/mall/products" class="sub-menu-item">
                <i class="el-icon-goods sub-menu-icon"></i>
                <span slot="title">商品管理</span>
              </el-menu-item>
              <!-- 分类管理 -->
              <el-menu-item index="/mall/categories" class="sub-menu-item">
                <i class="el-icon-menu sub-menu-icon"></i>
                <span slot="title">分类管理</span>
              </el-menu-item>
              <!-- 订单管理 -->
              <el-menu-item index="/mall/orders" class="sub-menu-item">
                <i class="el-icon-document sub-menu-icon"></i>
                <span slot="title">订单管理</span>
              </el-menu-item>
              <!-- 闪购管理 -->
              <el-menu-item index="/mall/marketing/flash-sale" class="sub-menu-item">
                <i class="el-icon-lightning sub-menu-icon"></i>
                <span slot="title">闪购管理</span>
              </el-menu-item>
              <!-- 优惠券管理 -->
              <el-menu-item index="/mall/marketing/coupon" class="sub-menu-item">
                <i class="el-icon-present sub-menu-icon"></i>
                <span slot="title">优惠券管理</span>
              </el-menu-item>
              <!-- 内容管理 -->
              <el-menu-item index="/mall/content" class="sub-menu-item">
                <i class="el-icon-picture sub-menu-icon"></i>
                <span slot="title">Banner管理</span>
              </el-menu-item>
              <!-- 用户地址管理 -->
              <el-menu-item index="/mall/users" class="sub-menu-item">
                <i class="el-icon-location sub-menu-icon"></i>
                <span slot="title">用户地址管理</span>
              </el-menu-item>
            </el-submenu>

          </el-menu>
        </el-aside>

        <!-- 主内容区 -->
        <el-main class="layout-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { getUserInfo } from '@/api/auth'

export default {
  name: 'AdminLayout',
  data() {
    return {
      userInfo: null
    }
  },
  created() {
    this.loadUserInfo()
  },
  methods: {
    async loadUserInfo() {
      try {
        const response = await getUserInfo()

        // 检查响应格式，适配不同的API响应格式
        if (response && response.data) {
          const responseData = response.data

          // 处理标准格式：{ success: true, data: {...} }
          if (responseData.success === true && responseData.data) {
            this.userInfo = responseData.data
          }
          // 处理其他可能的格式
          else if (responseData.id) {
            this.userInfo = responseData
          }
          else if (responseData.code === 200 && responseData.data) {
            this.userInfo = responseData.data
          }
          else {
            // 静默处理无法识别的格式
          }
        } else {
          // 静默处理空数据
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        if (error.response && error.response.status === 401) {
          this.$message.error('用户未认证，需要重新登录')
          // 可以在这里添加重定向到登录页面的逻辑
          // this.$router.push('/login')
        } else {
          this.$message.error('获取用户信息失败，请稍后重试')
        }
      }
    },

    handleCommand(command) {
      if (command === 'logout') {
        this.logout()
      }
    },

    logout() {
      this.$confirm('确定要退出登录吗？', '确认退出', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        localStorage.removeItem('admin_token')
        this.$router.replace('/login')
        this.$message.success('退出登录成功')
      }).catch(() => {
        // 用户取消
      })
    }
  }
}
</script>

<style scoped>
/* 导入Inter字体 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* 全局样式 */
.admin-layout {
  font-family: 'Inter', sans-serif;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
  z-index: -1;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(3xl);
  animation: float 8s ease-in-out infinite;
}

.bg-circle-1 {
  top: -10%;
  left: -10%;
  width: 400px;
  height: 400px;
  background-color: rgba(255, 107, 139, 0.1);
}

.bg-circle-2 {
  bottom: -10%;
  right: -10%;
  width: 500px;
  height: 500px;
  background-color: rgba(114, 46, 209, 0.1);
  animation-delay: -2s;
}

.bg-circle-3 {
  top: 50%;
  right: 20%;
  width: 200px;
  height: 200px;
  background-color: rgba(255, 107, 139, 0.05);
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

/* 布局容器 */
.layout-container {
  min-height: 100vh;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 0;
  margin: 0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 头部样式 */
.layout-header {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(255, 107, 139, 0.1);
  transition: all 0.3s ease;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  backdrop-filter: blur(10px);
  width: 100%;
}

.header-content {
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  align-items: center;
  gap: 20px;
}

/* 品牌标识 - 左侧 */
.logo {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  margin-right: auto;
  margin-left: -10px;
}

/* 系统描述 - 居中 */
.header-description {
  flex: 1;
  text-align: center;
  padding: 0 20px;
  transition: all 0.3s ease;
}

/* 用户信息 - 右侧 */
.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
  margin-left: auto;
}

.layout-header:hover {
  box-shadow: 0 6px 30px rgba(255, 107, 139, 0.15);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  gap: 30px;
}

/* Logo样式 */
.logo {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.logo-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  padding: 8px 0;
}

.logo-link:hover {
  transform: translateY(-3px);
}

.logo-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(255, 107, 139, 0.2);
  background: linear-gradient(135deg, #FF6B8B 0%, #722ED1 100%);
  border-radius: 50%;
  margin-right: 30px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.logo-icon::before {
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

.logo-link:hover .logo-icon {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 8px 28px rgba(255, 107, 139, 0.35);
}

.logo-heart {
  font-size: 18px;
  color: white;
  transition: all 0.3s ease;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.logo-text {
  display: flex;
  align-items: center;
}

.logo-main {
  font-size: 20px;
  font-weight: 700;
  color: #424242;
  transition: all 0.3s ease;
  letter-spacing: 0;
}

.logo-sub {
  font-size: 12px;
  color: #9E9E9E;
  transition: all 0.3s ease;
  margin-top: 2px;
  letter-spacing: 0.5px;
}

.logo-link:hover .logo-main {
  color: #FF6B8B;
  text-shadow: 0 1px 3px rgba(255, 107, 139, 0.3);
}

.logo-link:hover .logo-sub {
  color: #722ED1;
}

/* 系统描述 */
.header-description {
  flex: 1;
  text-align: center;
  padding: 0 30px;
  transition: all 0.3s ease;
}

.description-text {
  margin: 0;
  font-size: 14px;
  color: #757575;
  font-weight: 400;
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
}

/* 右侧用户信息 */
.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
}

/* 用户信息 */
.user-info {
  transition: all 0.3s ease;
}

.user-dropdown {
  transition: all 0.3s ease;
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-radius: 24px;
  background-color: rgba(255, 255, 255, 0.8);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
  border: 1px solid rgba(255, 107, 139, 0.1);
}

.user-avatar:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 4px 16px rgba(255, 107, 139, 0.15);
  border-color: rgba(255, 107, 139, 0.3);
}

.avatar-img {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #424242;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.user-arrow {
  font-size: 12px;
  color: #9E9E9E;
  transition: all 0.3s ease;
  transition: transform 0.3s ease;
}

.user-avatar:hover .user-arrow {
  transform: rotate(180deg);
  color: #FF6B8B;
}

/* 登录按钮 */
:deep(.el-button--primary.is-plain) {
  border-color: #FF6B8B;
  color: #FF6B8B;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border-radius: 20px;
  padding: 8px 24px;
  font-weight: 500;
}

:deep(.el-button--primary.is-plain:hover) {
  border-color: #722ED1;
  background-color: #722ED1;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(114, 46, 209, 0.3);
}

/* 下拉菜单样式 */
:deep(.el-dropdown-menu) {
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18) !important;
  overflow: hidden;
  border: none !important;
  margin-top: 8px !important;
  animation: dropdownFadeIn 0.3s ease-out;
}

/* 对话框样式 - 完全移除所有遮罩层 */
:deep(.el-dialog__wrapper) {
  background-color: transparent !important;
  animation: none !important;
  transition: none !important;
  opacity: 1 !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

:deep(.el-dialog) {
  border-radius: 16px !important;
  overflow: hidden;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2) !important;
  animation: dialogFadeIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* 确保遮罩层完全透明 */
:deep(.v-modal) {
  background-color: transparent !important;
  animation: none !important;
  transition: none !important;
  opacity: 0 !important;
  display: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

/* 额外的遮罩层样式覆盖 */
:deep(.el-dialog__wrapper.is-visible) {
  background-color: transparent !important;
  animation: none !important;
  transition: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

:deep(.v-modal-enter),
:deep(.v-modal-leave-active) {
  background-color: transparent !important;
  animation: none !important;
  transition: none !important;
  opacity: 0 !important;
  display: none !important;
}

/* 确保页面背景不受影响 */
.admin-layout {
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.layout-container {
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.layout-main {
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

@keyframes dialogFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

:deep(.el-dropdown-item) {
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  padding: 12px 24px !important;
  font-size: 14px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

:deep(.el-dropdown-item:last-child) {
  border-bottom: none;
}

:deep(.el-dropdown-item:hover) {
  background-color: rgba(255, 107, 139, 0.08) !important;
  color: #FF6B8B;
  transform: translateX(8px);
}

:deep(.el-dropdown-item i) {
  margin-right: 10px;
  transition: all 0.3s ease;
}

:deep(.el-dropdown-item:hover i) {
  transform: scale(1.2) rotate(5deg);
  color: #722ED1;
}

/* 侧边栏样式 */
.layout-aside {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 249, 250, 0.98) 100%);
  border-right: 1px solid rgba(255, 107, 139, 0.1);
  box-shadow: 2px 0 24px rgba(255, 107, 139, 0.12);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  height: 100%;
  overflow-y: auto;
  flex-shrink: 0;
}

.layout-aside::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(180deg, transparent, rgba(255, 107, 139, 0.1), transparent);
}

.layout-menu {
  border-right: none;
  height: calc(100% - 80px);
  margin: 64px 16px 16px 16px;
  border-radius: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.95) 100%);
  box-shadow: 0 6px 28px rgba(255, 107, 139, 0.12);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 1px solid rgba(255, 107, 139, 0.08);
}

.layout-menu:hover {
  box-shadow: 0 8px 32px rgba(255, 107, 139, 0.15);
  transform: translateY(-2px);
}

/* 侧边栏菜单滚动条 */
.layout-menu::-webkit-scrollbar {
  width: 8px;
}

.layout-menu::-webkit-scrollbar-track {
  background: linear-gradient(180deg, transparent, rgba(255, 107, 139, 0.05), transparent);
  border-radius: 12px;
  margin: 15px;
}

.layout-menu::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, rgba(255, 107, 139, 0.25) 0%, rgba(114, 46, 209, 0.25) 100%);
  border-radius: 12px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 2px solid rgba(255, 255, 255, 0.8);
}

.layout-menu::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, rgba(255, 107, 139, 0.35) 0%, rgba(114, 46, 209, 0.35) 100%);
  transform: scaleX(1.1);
  box-shadow: 0 2px 8px rgba(255, 107, 139, 0.2);
}

/* 菜单项样式 */
.menu-item {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  margin: 10px 16px;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  border: 1px solid transparent;
}

.menu-item:hover {
  background-color: rgba(255, 107, 139, 0.08);
  transform: translateX(8px);
  border-color: rgba(255, 107, 139, 0.2);
  box-shadow: 0 4px 16px rgba(255, 107, 139, 0.12);
}

.menu-item.is-active {
  background-color: rgba(255, 107, 139, 0.12);
  border-color: rgba(255, 107, 139, 0.3);
  box-shadow: 0 6px 20px rgba(255, 107, 139, 0.15);
}

.menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(135deg, #FF6B8B 0%, #722ED1 100%);
  border-radius: 0 4px 4px 0;
  box-shadow: 0 0 12px rgba(255, 107, 139, 0.4);
}

.menu-icon {
  font-size: 20px;
  width: 32px;
  text-align: center;
  margin-right: 18px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  z-index: 1;
}

.menu-item.is-active .menu-icon {
  color: #FF6B8B;
  transform: scale(1.15) rotate(5deg);
  text-shadow: 0 2px 8px rgba(255, 107, 139, 0.4);
}

/* 子菜单项样式 */
.sub-menu-item {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  margin: 6px 20px;
  border-radius: 10px;
  position: relative;
  border: 1px solid transparent;
  padding-left: 12px !important;
}

.sub-menu-item:hover {
  background-color: rgba(255, 107, 139, 0.06);
  transform: translateX(6px);
  border-color: rgba(255, 107, 139, 0.15);
  box-shadow: 0 3px 12px rgba(255, 107, 139, 0.09);
}

.sub-menu-item.is-active {
  background-color: rgba(255, 107, 139, 0.09);
  border-color: rgba(255, 107, 139, 0.25);
  box-shadow: 0 4px 16px rgba(255, 107, 139, 0.12);
}

.sub-menu-icon {
  font-size: 18px;
  width: 28px;
  text-align: center;
  margin-right: 14px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.sub-menu-item.is-active .sub-menu-icon {
  color: #722ED1;
  transform: scale(1.1) rotate(3deg);
  text-shadow: 0 1px 4px rgba(114, 46, 209, 0.3);
}

/* 深层子菜单项样式 */
.deep-sub-menu-item {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  margin: 4px 24px;
  border-radius: 8px;
  position: relative;
  border: 1px solid transparent;
  padding-left: 16px !important;
}

.deep-sub-menu-item:hover {
  background-color: rgba(255, 107, 139, 0.04);
  transform: translateX(4px);
  border-color: rgba(255, 107, 139, 0.1);
  box-shadow: 0 2px 8px rgba(255, 107, 139, 0.06);
}

.deep-sub-menu-item.is-active {
  background-color: rgba(255, 107, 139, 0.07);
  border-color: rgba(255, 107, 139, 0.2);
  box-shadow: 0 3px 12px rgba(255, 107, 139, 0.09);
}

.deep-sub-menu-icon {
  font-size: 16px;
  width: 24px;
  text-align: center;
  margin-right: 10px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.deep-sub-menu-item.is-active .deep-sub-menu-icon {
  color: #FF6B8B;
  transform: scale(1.05) rotate(2deg);
  text-shadow: 0 1px 3px rgba(255, 107, 139, 0.3);
}

/* 主内容区样式 */
.layout-main {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(245, 245, 245, 0.96) 100%);
  padding: 48px;
  overflow-y: auto;
  border-radius: 0 20px 20px 0;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  box-shadow: inset 2px 0 20px rgba(0, 0, 0, 0.03);
  flex: 1;
  min-width: 0;
  height: 100%;
}

.layout-main::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 107, 139, 0.1), transparent);
}

.layout-main:hover {
  box-shadow: inset 2px 0 24px rgba(0, 0, 0, 0.04);
}

/* 自定义滚动条 */
.layout-main::-webkit-scrollbar {
  width: 10px;
}

.layout-main::-webkit-scrollbar-track {
  background: rgba(255, 107, 139, 0.1);
  border-radius: 8px;
  margin: 10px;
}

.layout-main::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, rgba(255, 107, 139, 0.3) 0%, rgba(114, 46, 209, 0.3) 100%);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.layout-main::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, rgba(255, 107, 139, 0.4) 0%, rgba(114, 46, 209, 0.4) 100%);
  transform: scaleX(1.1);
}

/* 动画效果 */
.hover-scale {
  transition: transform 0.3s ease;
}

.hover-scale:hover {
  transform: scale(1.03);
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .layout-container {
    margin: 0;
    border-radius: 0;
  }

  .layout-header {
    padding: 0 20px;
  }

  .layout-main {
    padding: 20px;
  }

  .logo span {
    font-size: 14px;
  }

  .logo .w-10 {
    width: 8px;
    height: 8px;
  }

  .logo .w-10 i {
    font-size: 14px;
  }
}
</style>