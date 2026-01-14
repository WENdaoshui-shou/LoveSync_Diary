<template>
  <div
    class="font-inter bg-neutral-100 text-neutral-800 min-h-screen flex flex-col overflow-x-hidden relative scroll-smooth">
    <!-- 背景装饰元素 -->
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -left-40 w-80 h-80 bg-primary/10 rounded-full filter blur-3xl float-animation"></div>
      <div class="absolute -bottom-20 -right-20 w-80 h-80 bg-secondary/10 rounded-full filter blur-3xl float-animation"
        style="animation-delay: -2s;"></div>
    </div>

    <!-- 导航栏 -->
    <header class="fixed w-full top-0 z-50 transition-all duration-300 bg-white/95 backdrop-blur-md shadow-sm py-3">
      <div class="container mx-auto px-4 flex items-center justify-between">
        <!-- 品牌标识 -->
        <router-link to="/" class="flex items-center space-x-2">
          <div class="w-10 h-10 rounded-full bg-gradient-love flex items-center justify-center text-white shadow-md">
            <i class="fa-solid fa-heart text-xl"></i>
          </div>
          <span class="text-xl font-bold text-neutral-800 tracking-tight">LoveSync</span>
        </router-link>
        <!-- 桌面端导航菜单 -->
        <nav class="hidden md:flex items-center space-x-6">
          <router-link to="/community"
            class="text-neutral-700 hover:text-primary transition-custom font-medium px-1 py-2 border-b-2 border-transparent hover:border-primary">爱享公社</router-link>
          <router-link to="/moments"
            class="text-primary font-medium px-1 py-2 border-b-2 border-primary">心动轨迹</router-link>
          <router-link to="/photo-album"
            class="text-neutral-700 hover:text-primary transition-custom font-medium px-1 py-2 border-b-2 border-transparent hover:border-primary">心跳相簿</router-link>
          <router-link to="/lovesync"
            class="text-neutral-700 hover:text-primary transition-custom font-medium px-1 py-2 border-b-2 border-transparent hover:border-primary">双人日记</router-link>
        </nav>
        <!-- 用户操作区 -->
        <div class="flex items-center space-x-4">
          <button
            class="flex items-center space-x-2 px-5 py-2 rounded-full bg-gradient-love text-white hover:opacity-90 transition-custom shadow-md hover:shadow-lg">
            <i class="fa-solid fa-pencil"></i>
            <span>发布动态</span>
          </button>
          <!-- 用户头像与下拉菜单 -->
          <div class="relative" id="userDropdown">
            <div class="w-10 h-10 rounded-full overflow-hidden border-2 border-primary cursor-pointer shadow-sm"
              id="userAvatar">
              <img :src="userAvatar" alt="用户头像" class="w-full h-full object-cover">
            </div>
            <div class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl py-2 z-50 hidden" id="userOptions">
              <router-link to="/personal-center"
                class="block px-4 py-2 text-neutral-700 hover:bg-neutral-50 transition-custom flex items-center">
                <i class="fa-solid fa-user mr-2 w-5 text-center"></i>主页
              </router-link>
              <router-link to="/message"
                class="block px-4 py-2 text-neutral-700 hover:bg-neutral-50 transition-custom flex items-center">
                <i class="fa-solid fa-bookmark mr-2 w-5 text-center"></i>消息
              </router-link>
              <router-link to="/settings"
                class="block px-4 py-2 text-neutral-700 hover:bg-neutral-50 transition-custom flex items-center">
                <i class="fa-solid fa-cog mr-2 w-5 text-center"></i>设置
              </router-link>
              <div class="border-t border-neutral-200 my-1"></div>
              <a href="#" @click="logout"
                class="block px-4 py-2 text-red-500 hover:bg-red-50 transition-custom flex items-center">
                <i class="fa-solid fa-sign-out mr-2 w-5 text-center"></i>退出登录
              </a>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="flex-grow pt-24 pb-16 relative z-10">
      <div class="container mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 左侧边栏 -->
          <div class="md:col-span-1">
            <!-- 发布动态卡片 -->
            <div class="bg-white rounded-xl shadow-lg p-4 hover-scale">
              <div class="flex items-start space-x-3">
                <div class="w-10 h-10 rounded-full overflow-hidden">
                  <img :src="userAvatar" alt="用户头像" class="w-full h-full object-cover">
                </div>
                <div class="flex-1">
                  <button
                    class="w-full text-left p-3 rounded-full bg-neutral-100 hover:bg-neutral-200 transition-custom text-sm text-neutral-700">
                    分享你的心动时刻...
                  </button>
                  <div class="flex justify-between mt-3">
                    <button
                      class="flex items-center space-x-1 text-primary/70 hover:text-primary transition-custom px-3 py-1 rounded-full text-sm">
                      <i class="fa-solid fa-image"></i>
                      <span>图片</span>
                    </button>
                    <button
                      class="flex items-center space-x-1 text-primary/70 hover:text-primary transition-custom px-3 py-1 rounded-full text-sm">
                      <i class="fa-solid fa-video"></i>
                      <span>视频</span>
                    </button>
                    <button
                      class="flex items-center space-x-1 text-primary/70 hover:text-primary transition-custom px-3 py-1 rounded-full text-sm">
                      <i class="fa-solid fa-music"></i>
                      <span>音乐</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 热门话题 -->
            <div class="bg-white rounded-xl shadow-lg p-4 mt-6 hover-scale">
              <h3 class="text-lg font-semibold text-neutral-900 mb-4">热门话题</h3>
              <div class="space-y-3">
                <div class="flex items-center justify-between p-2 hover:bg-neutral-50 rounded-lg transition-custom">
                  <div class="flex items-center space-x-2">
                    <i class="fa-solid fa-fire text-primary"></i>
                    <span class="text-neutral-800">#恋爱一周年</span>
                  </div>
                  <span class="text-xs text-neutral-500">1.2k</span>
                </div>
                <div class="flex items-center justify-between p-2 hover:bg-neutral-50 rounded-lg transition-custom">
                  <div class="flex items-center space-x-2">
                    <i class="fa-solid fa-fire text-primary"></i>
                    <span class="text-neutral-800">#情侣旅行</span>
                  </div>
                  <span class="text-xs text-neutral-500">892</span>
                </div>
                <div class="flex items-center justify-between p-2 hover:bg-neutral-50 rounded-lg transition-custom">
                  <div class="flex items-center space-x-2">
                    <i class="fa-solid fa-fire text-primary"></i>
                    <span class="text-neutral-800">#爱情誓言</span>
                  </div>
                  <span class="text-xs text-neutral-500">645</span>
                </div>
                <div class="flex items-center justify-between p-2 hover:bg-neutral-50 rounded-lg transition-custom">
                  <div class="flex items-center space-x-2">
                    <i class="fa-solid fa-fire text-primary"></i>
                    <span class="text-neutral-800">#双人日记</span>
                  </div>
                  <span class="text-xs text-neutral-500">512</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 中间内容区 -->
          <div class="md:col-span-2">
            <!-- 动态列表 -->
            <div class="space-y-6">
              <!-- 动态1 -->
              <div class="bg-white rounded-xl shadow-lg overflow-hidden post-card" v-for="moment in moments"
                :key="moment.id">
                <div class="p-6">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                      <div class="w-10 h-10 rounded-full overflow-hidden">
                        <img :src="moment.avatar" alt="发布者头像" class="w-full h-full object-cover">
                      </div>
                      <div>
                        <h4 class="font-semibold text-neutral-900">{{ moment.author }}</h4>
                        <p class="text-neutral-500 text-xs">{{ moment.time }}</p>
                      </div>
                    </div>
                    <button class="text-neutral-400 hover:text-neutral-700 transition-custom">
                      <i class="fa-solid fa-ellipsis-h"></i>
                    </button>
                  </div>
                  <div class="mt-4">
                    <p class="text-neutral-800">{{ moment.content }}</p>
                  </div>
                  <div class="mt-4 grid grid-cols-2 gap-2">
                    <img v-for="(img, index) in moment.images" :key="index" :src="img" alt="动态图片"
                      class="rounded-lg w-full h-40 object-cover hover-scale">
                  </div>
                  <div class="mt-4 flex justify-between items-center">
                    <div class="flex space-x-4">
                      <button
                        class="flex items-center space-x-1 text-neutral-500 hover:text-primary transition-custom like-btn">
                        <i class="fa-regular fa-heart"></i>
                        <span>{{ moment.likes }}</span>
                      </button>
                      <button @click="toggleComments(moment.id)"
                        class="flex items-center space-x-1 text-neutral-500 hover:text-primary transition-custom comment-btn">
                        <i class="fa-regular fa-comment"></i>
                        <span>{{ moment.commentsCount }}</span>
                      </button>
                    </div>
                    <button class="flex items-center space-x-1 text-neutral-500 hover:text-primary transition-custom">
                      <i class="fa-regular fa-share-from-square"></i>
                      <span>分享</span>
                    </button>
                  </div>
                </div>
                <!-- 评论区域 -->
                <div v-if="moment.showComments" class="bg-neutral-50 p-4 border-t border-neutral-100 comment-section">
                  <div class="space-y-4">
                    <!-- 评论1 -->
                    <div class="flex space-x-3 comment-slide" v-for="comment in moment.comments" :key="comment.id">
                      <div class="w-8 h-8 rounded-full overflow-hidden">
                        <img :src="comment.avatar" alt="评论者头像" class="w-full h-full object-cover">
                      </div>
                      <div class="flex-1">
                        <div class="bg-white rounded-lg p-3">
                          <div class="flex justify-between items-center">
                            <h5 class="font-medium text-sm text-neutral-900">{{ comment.author }}</h5>
                            <span class="text-neutral-400 text-xs">{{ comment.time }}</span>
                          </div>
                          <p class="text-neutral-700 text-sm mt-1">{{ comment.content }}</p>
                        </div>
                        <div class="flex space-x-3 mt-2">
                          <button class="text-neutral-500 hover:text-primary text-xs transition-custom">
                            <i class="fa-regular fa-heart"></i> {{ comment.likes }}
                          </button>
                          <button class="text-neutral-500 hover:text-primary text-xs transition-custom">
                            回复
                          </button>
                        </div>
                      </div>
                    </div>
                    <!-- 发表评论 -->
                    <div class="flex space-x-3 mt-2">
                      <div class="w-8 h-8 rounded-full overflow-hidden">
                        <img :src="userAvatar" alt="用户头像" class="w-full h-full object-cover">
                      </div>
                      <div class="flex-1 relative">
                        <input type="text" placeholder="写下你的评论..."
                          class="w-full border border-neutral-200 rounded-full pl-4 pr-10 py-2 focus:outline-none focus:ring-2 focus:ring-primary/50 form-input-focus text-sm">
                        <button class="absolute right-2 top-1/2 -translate-y-1/2 text-primary">
                          <i class="fa-solid fa-paper-plane"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="bg-white border-t border-neutral-200 py-8">
      <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <a href="#" class="flex items-center space-x-2">
            <div class="w-10 h-10 rounded-full bg-gradient-love flex items-center justify-center text-white shadow-md">
              <i class="fa-solid fa-heart text-xl"></i>
            </div>
            <span class="text-xl font-bold text-neutral-800 tracking-tight">LoveSync</span>
          </a>
          <div class="text-neutral-500 text-sm">
            &copy; 2025 LoveSync. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'Moments',
  data () {
    return {
      userAvatar: 'https://picsum.photos/200/200?random=1',
      moments: [
        {
          id: 1,
          author: '小甜甜和小帅帅',
          avatar: 'https://picsum.photos/200/200?random=5',
          time: '2小时前',
          content: '今天是我们恋爱一周年的日子，一起去了我们第一次约会的餐厅，回忆满满💕 #恋爱一周年纪念#',
          images: [
            'https://picsum.photos/600/400?random=10',
            'https://picsum.photos/600/400?random=11'
          ],
          likes: 128,
          commentsCount: 24,
          comments: [
            {
              id: 1,
              author: '恋爱小助手',
              avatar: 'https://picsum.photos/200/200?random=6',
              time: '1小时前',
              content: '一周年快乐！好羡慕你们呀，希望你们能一直幸福下去~',
              likes: 16
            },
            {
              id: 2,
              author: '爱情故事',
              avatar: 'https://picsum.photos/200/200?random=7',
              time: '50分钟前',
              content: '餐厅看起来很不错啊，是哪家呢？也想和另一半去体验一下~',
              likes: 8
            }
          ],
          showComments: false
        },
        {
          id: 2,
          author: '旅行情侣',
          avatar: 'https://picsum.photos/200/200?random=8',
          time: '昨天',
          content: '第一次一起出国旅行，泰国普吉岛真的太美了！和你一起看海，一起探索新的地方，这就是我想要的生活~ #情侣旅行#',
          images: [
            'https://picsum.photos/600/400?random=20',
            'https://picsum.photos/600/400?random=21',
            'https://picsum.photos/600/400?random=22'
          ],
          likes: 256,
          commentsCount: 42,
          comments: [
            {
              id: 3,
              author: '环球旅行者',
              avatar: 'https://picsum.photos/200/200?random=9',
              time: '18小时前',
              content: '普吉岛确实是个好地方！有什么推荐的餐厅或景点吗？',
              likes: 12
            },
            {
              id: 4,
              author: '海边漫步',
              avatar: 'https://picsum.photos/200/200?random=10',
              time: '16小时前',
              content: '照片拍得真美！你们是自由行还是跟团呢？',
              likes: 9
            }
          ],
          showComments: false
        },
        {
          id: 3,
          author: '美食爱好者',
          avatar: 'https://picsum.photos/200/200?random=11',
          time: '3天前',
          content: '周末一起做了一顿丰盛的晚餐，虽然过程有些曲折，但结果很完美~ 两个人一起做饭的感觉真好！ #情侣厨艺大比拼#',
          images: [
            'https://picsum.photos/600/400?random=30',
            'https://picsum.photos/600/400?random=31'
          ],
          likes: 89,
          commentsCount: 15,
          comments: [
            {
              id: 5,
              author: '厨艺达人',
              avatar: 'https://picsum.photos/200/200?random=12',
              time: '2天前',
              content: '看起来好美味！能分享一下食谱吗？',
              likes: 23
            }
          ],
          showComments: false
        }
      ]
    }
  },
  methods: {
    logout () {
      // 调用Vuex的登出action
      this.$store.dispatch('logout')
      this.$router.push('/login')
    },
    toggleComments (momentId) {
      const moment = this.moments.find(m => m.id === momentId)
      if (moment) {
        moment.showComments = !moment.showComments
      }
    }
  }
}
</script>
