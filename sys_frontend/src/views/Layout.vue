<template>
  <el-container class="layout-container">
    <!-- 头部 -->
    <el-header class="layout-header">
      <div class="header-content">
        <div class="logo">
          <h2>LoveSync 管理后台</h2>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
              <i class="el-icon-user"></i>
              {{ userInfo?.name || '管理员' }}
              <i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="200px" class="layout-aside">
        <el-menu :default-active="$route.path" class="layout-menu" router background-color="#304156"
          text-color="#bfcbd9" active-text-color="#409EFF">
          <el-menu-item index="/">
            <i class="el-icon-s-home"></i>
            <span slot="title">首页</span>
          </el-menu-item>

          <el-menu-item index="/users">
            <i class="el-icon-user"></i>
            <span slot="title">用户管理</span>
          </el-menu-item>

          <el-menu-item index="/moments">
            <i class="el-icon-news"></i>
            <span slot="title">动态管理</span>
          </el-menu-item>

          <el-submenu index="/community">
            <template slot="title">
              <i class="el-icon-s-grid"></i>
              <span>社区管理</span>
            </template>
            <el-menu-item index="/community/events">
              <i class="el-icon-date"></i>
              <span slot="title">社区活动</span>
            </el-menu-item>
            <el-menu-item index="/community/articles">
              <i class="el-icon-document"></i>
              <span slot="title">文章专栏</span>
            </el-menu-item>
            <el-menu-item index="/community/topics">
              <i class="el-icon-top"></i>
              <span slot="title">热门话题</span>
            </el-menu-item>
            <el-menu-item index="/community/reports">
              <i class="el-icon-warning-outline"></i>
              <span slot="title">举报管理</span>
            </el-menu-item>
          </el-submenu>

          <el-submenu index="/couple">
            <template slot="title">
              <i class="el-icon-connection"></i>
              <span>情侣管理</span>
            </template>
            <el-menu-item index="/couple/recommended">
              <i class="el-icon-sunny"></i>
              <span slot="title">推荐情侣管理</span>
            </el-menu-item>
            <el-menu-item index="/couple/places">
              <i class="el-icon-s-flag"></i>
              <span slot="title">地点管理</span>
            </el-menu-item>
            <el-menu-item index="/couple/tests">
              <i class="el-icon-question"></i>
              <span slot="title">爱情测试管理</span>
            </el-menu-item>
            <el-menu-item index="/couple/games">
              <i class="el-icon-s-grid"></i>
              <span slot="title">情侣游戏管理</span>
            </el-menu-item>
          </el-submenu>

          <el-submenu index="/mall">
            <template slot="title">
              <i class="el-icon-shopping-cart"></i>
              <span>商城管理</span>
            </template>
            <!-- 商品管理 -->
            <el-menu-item index="/mall/products">
              <i class="el-icon-goods"></i>
              <span slot="title">商品管理</span>
            </el-menu-item>
            <!-- 分类管理 -->
            <el-menu-item index="/mall/categories">
              <i class="el-icon-menu"></i>
              <span slot="title">分类管理</span>
            </el-menu-item>
            <!-- 订单管理 -->
            <el-menu-item index="/mall/orders">
              <i class="el-icon-document"></i>
              <span slot="title">订单管理</span>
            </el-menu-item>
            <!-- 营销管理 -->
            <el-submenu index="/mall/marketing">
              <template slot="title">
                <i class="el-icon-s-marketing"></i>
                <span>营销管理</span>
              </template>
              <el-menu-item index="/mall/marketing/flash-sale">
                <i class="el-icon-lightning"></i>
                <span slot="title">闪购管理</span>
              </el-menu-item>
              <el-menu-item index="/mall/marketing/coupon">
                <i class="el-icon-ticket"></i>
                <span slot="title">优惠券管理</span>
              </el-menu-item>
            </el-submenu>
            <!-- 内容管理 -->
            <el-menu-item index="/mall/content">
              <i class="el-icon-picture"></i>
              <span slot="title">Banner管理</span>
            </el-menu-item>
            <!-- 用户地址管理 -->
            <el-menu-item index="/mall/users">
              <i class="el-icon-user"></i>
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
.layout-container {
  height: 100vh;
}

.layout-header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 21, 41, 0.08);
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.logo h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}

.header-right {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  cursor: pointer;
  color: #409EFF;
}

.layout-aside {
  background-color: #304156;
  border-right: 1px solid #e6e6e6;
}

.layout-menu {
  border-right: none;
  height: calc(100vh - 60px);
}

.layout-main {
  background-color: #f5f5f5;
  padding: 20px;
}
</style>