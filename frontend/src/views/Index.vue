<template>
  <div class="index-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo">
          <h1>LoveSync</h1>
        </div>
        <el-menu :default-active="activeMenu" class="nav-menu" mode="horizontal" @select="handleMenuSelect">
          <el-menu-item index="index">首页</el-menu-item>
          <el-menu-item index="moments">动态</el-menu-item>
          <el-menu-item index="lovesync">双人日记</el-menu-item>
          <el-menu-item index="photo_album">相册</el-menu-item>
          <el-menu-item index="mall">商城</el-menu-item>
        </el-menu>
        <div class="user-info">
          <el-dropdown @command="handleDropdownCommand">
            <span class="user-avatar">
              <el-avatar :size="40" :src="userAvatar">
                {{ user.name ? user.name.charAt(0) : 'U' }}
              </el-avatar>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="personal_center">个人中心</el-dropdown-item>
              <el-dropdown-item command="settings">设置</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <!-- 主体内容 -->
    <el-main class="main">
      <div class="content-wrapper">
        <!-- 左侧边栏 -->
        <el-aside class="sidebar">
          <div class="sidebar-section">
            <h3>快捷导航</h3>
            <el-menu class="sidebar-menu" @select="handleSidebarSelect">
              <el-menu-item index="personal_center">
                <i class="el-icon-user"></i>
                <span slot="title">个人中心</span>
              </el-menu-item>
              <el-menu-item index="couple">
                <i class="el-icon-heart"></i>
                <span slot="title">我的伴侣</span>
              </el-menu-item>
              <el-menu-item index="note">
                <i class="el-icon-document"></i>
                <span slot="title">我的日记</span>
              </el-menu-item>
              <el-menu-item index="favorites">
                <i class="el-icon-star-on"></i>
                <span slot="title">我的收藏</span>
              </el-menu-item>
              <el-menu-item index="message">
                <i class="el-icon-message"></i>
                <span slot="title">消息通知</span>
              </el-menu-item>
            </el-menu>
          </div>

          <div class="sidebar-section">
            <h3>热门推荐</h3>
            <div class="hot-recommend">
              <div class="hot-item" v-for="item in hotItems" :key="item.id">
                <el-image :src="item.image" :fit="'cover'"
                  style="width: 100%; height: 80px; border-radius: 8px;"></el-image>
                <p class="hot-title">{{ item.title }}</p>
              </div>
            </div>
          </div>
        </el-aside>

        <!-- 中间内容区 -->
        <el-container class="main-content">
          <!-- 轮播图 -->
          <div class="banner-section">
            <el-carousel height="300px" indicator-position="outside">
              <el-carousel-item v-for="(item, index) in banners" :key="index">
                <el-image :src="item.image" :fit="'cover'" style="width: 100%; height: 300px;"></el-image>
              </el-carousel-item>
            </el-carousel>
          </div>

          <!-- 动态列表 -->
          <div class="moments-section">
            <div class="section-header">
              <h2>最新动态</h2>
              <el-button type="primary" @click="$router.push('/moments')">
                查看全部
              </el-button>
            </div>

            <div class="moments-list">
              <div class="moment-item" v-for="moment in moments" :key="moment.id">
                <div class="moment-header">
                  <el-avatar :size="40" :src="moment.user.avatar">
                    {{ moment.user.name.charAt(0) }}
                  </el-avatar>
                  <div class="moment-user-info">
                    <p class="moment-username">{{ moment.user.name }}</p>
                    <p class="moment-time">{{ formatTime(moment.created_at) }}</p>
                  </div>
                </div>

                <div class="moment-content">
                  <p>{{ moment.content }}</p>
                  <div class="moment-images" v-if="moment.moment_images && moment.moment_images.length">
                    <el-image v-for="(image, index) in moment.moment_images" :key="index" :src="image.image"
                      :fit="'cover'"
                      style="width: 100px; height: 100px; margin-right: 10px; border-radius: 8px;"></el-image>
                  </div>
                </div>

                <div class="moment-actions">
                  <el-button type="text" @click="handleLike(moment)">
                    <i :class="moment.liked ? 'el-icon-heart' : 'el-icon-heart-outline'"></i>
                    {{ moment.likes }} 点赞
                  </el-button>
                  <el-button type="text" @click="handleComment(moment)">
                    <i class="el-icon-chat-dot-round"></i>
                    {{ moment.comments }} 评论
                  </el-button>
                  <el-button type="text" @click="handleShare(moment)">
                    <i class="el-icon-share"></i>
                    分享
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 日记推荐 -->
          <div class="notes-section">
            <div class="section-header">
              <h2>热门日记</h2>
              <el-button type="primary" @click="$router.push('/note')">
                查看全部
              </el-button>
            </div>

            <div class="notes-grid">
              <div class="note-card" v-for="note in notes" :key="note.id">
                <div class="note-header">
                  <el-tag :color="note.mood_color">{{ note.mood_display_text }}</el-tag>
                  <el-icon :class="note.mood_icon"></el-icon>
                </div>
                <div class="note-content">
                  <p class="note-text">{{ note.context }}</p>
                </div>
                <div class="note-footer">
                  <span class="note-date">{{ formatTime(note.created_at) }}</span>
                  <el-button type="text" size="small" @click="handleViewNote(note)">
                    查看详情
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-container>

        <!-- 右侧边栏 -->
        <el-aside class="right-sidebar">
          <!-- 情侣信息 -->
          <div class="couple-section">
            <h3>我的伴侣</h3>
            <div class="couple-info" v-if="couple">
              <el-avatar :size="60" :src="couple.userAvatar">
                {{ couple.user.name.charAt(0) }}
              </el-avatar>
              <p class="couple-name">{{ couple.user.name }}</p>
              <p class="couple-joined">
                绑定于 {{ formatTime(couple.couple_joined_at) }}
              </p>
              <el-button type="primary" size="small" @click="$router.push('/couple')">
                情侣空间
              </el-button>
            </div>
            <div class="no-couple" v-else>
              <p>还没有绑定伴侣？</p>
              <el-button type="primary" size="small" @click="$router.push('/invite_partner')">
                邀请伴侣
              </el-button>
            </div>
          </div>

          <!-- 消息通知 -->
          <div class="notifications-section">
            <h3>消息通知</h3>
            <div class="notification-list">
              <div class="notification-item" v-for="notification in notifications" :key="notification.id">
                <el-badge :value="notification.unread" :max="99" v-if="notification.unread > 0">
                  <span class="notification-content">{{ notification.content }}</span>
                </el-badge>
                <span class="notification-content" v-else>{{ notification.content }}</span>
                <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
              </div>
            </div>
          </div>
        </el-aside>
      </div>
    </el-main>

    <!-- 底部 -->
    <el-footer class="footer">
      <p>&copy; 2026 LoveSync 情侣日记本. 保留所有权利.</p>
    </el-footer>
  </div>
</template>

<script>
export default {
  name: 'Index',
  data () {
    return {
      activeMenu: 'index',
      user: {
        name: '',
        avatar: ''
      },
      userAvatar: '',
      moments: [],
      notes: [],
      banners: [
        { id: 1, image: 'https://via.placeholder.com/1200x300?text=Banner+1' },
        { id: 2, image: 'https://via.placeholder.com/1200x300?text=Banner+2' },
        { id: 3, image: 'https://via.placeholder.com/1200x300?text=Banner+3' }
      ],
      hotItems: [
        { id: 1, title: '热门商品1', image: 'https://via.placeholder.com/200x100' },
        { id: 2, title: '热门商品2', image: 'https://via.placeholder.com/200x100' },
        { id: 3, title: '热门商品3', image: 'https://via.placeholder.com/200x100' }
      ],
      couple: null,
      notifications: [
        { id: 1, content: '你收到了一条新消息', created_at: new Date().toISOString(), unread: 1 },
        { id: 2, content: '你的伴侣发布了新动态', created_at: new Date().toISOString(), unread: 0 }
      ]
    }
  },
  created () {
    this.initData()
  },
  methods: {
    async initData () {
      try {
        // 获取用户信息
        const userData = await this.$store.dispatch('fetchUser')
        this.user = userData.user
        this.userAvatar = userData.userAvatar

        // 获取动态列表
        this.moments = await this.fetchMoments()

        // 获取日记列表
        this.notes = await this.fetchNotes()

        // 获取情侣信息
        this.couple = userData.couple
      } catch (error) {
        console.error('初始化数据失败:', error)
      }
    },

    async fetchMoments () {
      // 模拟API请求
      return [
        {
          id: 1,
          user: { name: '张三', avatar: '' },
          content: '今天和伴侣一起去看了电影，很开心！',
          created_at: new Date().toISOString(),
          likes: 12,
          comments: 3,
          moment_images: [],
          liked: false
        },
        {
          id: 2,
          user: { name: '李四', avatar: '' },
          content: '一起做了一顿丰盛的晚餐，味道不错！',
          created_at: new Date().toISOString(),
          likes: 8,
          comments: 2,
          moment_images: [
            { id: 1, image: 'https://via.placeholder.com/200x200' },
            { id: 2, image: 'https://via.placeholder.com/200x200' }
          ],
          liked: true
        }
      ]
    },

    async fetchNotes () {
      // 模拟API请求
      return [
        {
          id: 1,
          context: '今天是我们在一起的第100天，感觉时间过得真快！',
          created_at: new Date().toISOString(),
          mood: 'happy',
          mood_color: '#48BB78',
          mood_icon: 'el-icon-smile',
          mood_display_text: '开心的一天'
        },
        {
          id: 2,
          context: '一起去了海边，看到了美丽的日落，感觉很幸福！',
          created_at: new Date().toISOString(),
          mood: 'heart',
          mood_color: '#ED8936',
          mood_icon: 'el-icon-heart',
          mood_display_text: '心动时刻'
        }
      ]
    },

    handleMenuSelect (key, keyPath) {
      this.$router.push(`/${key}`)
    },

    handleSidebarSelect (key, keyPath) {
      this.$router.push(`/${key}`)
    },

    handleDropdownCommand (command) {
      if (command === 'logout') {
        this.$store.dispatch('logout')
        this.$router.push('/login')
      } else {
        this.$router.push(`/${command}`)
      }
    },

    formatTime (timeStr) {
      const date = new Date(timeStr)
      return date.toLocaleString()
    },

    handleLike (moment) {
      moment.liked = !moment.liked
      moment.likes += moment.liked ? 1 : -1
    },

    handleComment (moment) {
      this.$router.push(`/moments/${moment.id}/comments`)
    },

    handleShare (moment) {
      this.$message.success('分享成功')
    },

    handleViewNote (note) {
      this.$router.push(`/note/${note.id}`)
    }
  }
}
</script>

<style scoped>
.index-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
}

.logo h1 {
  margin: 0;
  color: var(--primary-color);
  font-size: 24px;
}

.nav-menu {
  flex: 1;
  margin: 0 40px;
}

.user-avatar {
  cursor: pointer;
}

.main {
  flex: 1;
  background-color: #f5f7fa;
  padding: 20px 0;
}

.content-wrapper {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  gap: 20px;
}

.sidebar {
  width: 200px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 20px;
}

.sidebar-section {
  margin-bottom: 30px;
}

.sidebar-section h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: var(--text-color);
}

.sidebar-menu {
  border-right: none;
}

.main-content {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 20px;
}

.right-sidebar {
  width: 250px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.couple-section,
.notifications-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 20px;
}

.couple-info {
  text-align: center;
}

.couple-name {
  margin: 10px 0 5px 0;
  font-weight: bold;
}

.couple-joined {
  margin: 0 0 15px 0;
  color: var(--text-color-secondary);
  font-size: 14px;
}

.no-couple {
  text-align: center;
  padding: 20px 0;
}

.banner-section {
  margin-bottom: 30px;
}

.moments-section,
.notes-section {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
}

.moment-item {
  background-color: #fafafa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.moment-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  gap: 10px;
}

.moment-user-info {
  flex: 1;
}

.moment-username {
  margin: 0;
  font-weight: bold;
}

.moment-time {
  margin: 0;
  font-size: 12px;
  color: var(--text-color-secondary);
}

.moment-content {
  margin-bottom: 15px;
}

.moment-images {
  display: flex;
  margin-top: 10px;
}

.moment-actions {
  display: flex;
  gap: 20px;
}

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.note-card {
  background-color: #fafafa;
  border-radius: 8px;
  padding: 15px;
  transition: transform 0.3s ease;
}

.note-card:hover {
  transform: translateY(-5px);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.note-content {
  margin-bottom: 15px;
}

.note-text {
  margin: 0;
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: var(--text-color-secondary);
}

.footer {
  background-color: white;
  text-align: center;
  padding: 20px 0;
  color: var(--text-color-secondary);
  border-top: 1px solid #e0e0e0;
}

@media (max-width: 1200px) {
  .right-sidebar {
    display: none;
  }
}

@media (max-width: 992px) {
  .sidebar {
    display: none;
  }

  .nav-menu {
    display: none;
  }
}
</style>
