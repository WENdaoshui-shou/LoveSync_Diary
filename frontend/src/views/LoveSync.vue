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
            class="text-neutral-700 hover:text-primary transition-custom font-medium px-1 py-2 border-b-2 border-transparent hover:border-primary">心动轨迹</router-link>
          <router-link to="/photo-album"
            class="text-neutral-700 hover:text-primary transition-custom font-medium px-1 py-2 border-b-2 border-transparent hover:border-primary">心跳相簿</router-link>
          <router-link to="/lovesync"
            class="text-primary font-medium px-1 py-2 border-b-2 border-primary">双人日记</router-link>
        </nav>
        <!-- 用户操作区 -->
        <div class="flex items-center space-x-4">
          <router-link to="/personal-center"
            class="block px-4 py-2 text-neutral-700 hover:bg-neutral-50 transition-custom flex items-center">
            <i class="fa-solid fa-user mr-2 w-5 text-center"></i>我的
          </router-link>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="flex-grow pt-24 pb-16 relative z-10">
      <div class="container mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 左侧边栏 -->
          <div class="md:col-span-1">
            <!-- 情侣信息卡片 -->
            <div class="bg-white rounded-xl shadow-lg p-4 hover-scale">
              <h3 class="text-lg font-semibold text-neutral-900 mb-4">我们的信息</h3>
              <div class="flex justify-between items-center mb-4">
                <div class="text-center">
                  <div class="w-12 h-12 rounded-full overflow-hidden mx-auto mb-2">
                    <img :src="userAvatar" alt="我的头像" class="w-full h-full object-cover">
                  </div>
                  <p class="text-sm font-medium">{{ myName }}</p>
                </div>
                <div class="text-primary">
                  <i class="fa-solid fa-heart text-xl"></i>
                </div>
                <div class="text-center">
                  <div class="w-12 h-12 rounded-full overflow-hidden mx-auto mb-2">
                    <img :src="partnerAvatar" alt="伴侣头像" class="w-full h-full object-cover">
                  </div>
                  <p class="text-sm font-medium">{{ partnerName }}</p>
                </div>
              </div>
              <div class="border-t border-neutral-200 pt-4">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm text-neutral-500">恋爱天数</span>
                  <span class="text-sm font-medium">{{ loveDays }}天</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-neutral-500">最近日记</span>
                  <span class="text-sm font-medium">今天</span>
                </div>
              </div>
            </div>

            <!-- 日记统计卡片 -->
            <div class="bg-white rounded-xl shadow-lg p-4 mt-6 hover-scale">
              <h3 class="text-lg font-semibold text-neutral-900 mb-4">日记统计</h3>
              <div class="space-y-3">
                <div class="flex justify-between items-center p-2 hover:bg-neutral-50 rounded-lg transition-custom">
                  <span class="text-sm text-neutral-700">总日记数</span>
                  <span class="text-primary font-medium">{{ totalDiaries }}</span>
                </div>
                <div class="flex justify-between items-center p-2 hover:bg-neutral-50 rounded-lg transition-custom">
                  <span class="text-sm text-neutral-700">我的贡献</span>
                  <span class="text-primary font-medium">{{ myDiaries }}</span>
                </div>
                <div class="flex justify-between items-center p-2 hover:bg-neutral-50 rounded-lg transition-custom">
                  <span class="text-sm text-neutral-700">伴侣贡献</span>
                  <span class="text-primary font-medium">{{ partnerDiaries }}</span>
                </div>
                <div class="h-1 bg-neutral-200 rounded-full overflow-hidden mt-4">
                  <div class="h-full bg-primary rounded-full" style="width: 60%"></div>
                </div>
                <div class="flex justify-between text-xs text-neutral-500 mt-1">
                  <span>{{ myName }}</span>
                  <span>{{ partnerName }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 中间内容区 -->
          <div class="md:col-span-2">
            <!-- 新建日记卡片 -->
            <div class="bg-white rounded-xl shadow-lg p-4 hover-scale">
              <h3 class="text-lg font-semibold text-neutral-900 mb-4">写日记</h3>
              <div class="space-y-4">
                <div>
                  <input type="text" placeholder="今天的标题..."
                    class="w-full border border-neutral-200 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary/50 form-input-focus text-sm">
                </div>
                <div>
                  <textarea placeholder="今天发生了什么有趣的事情？和伴侣一起分享吧..." rows="5"
                    class="w-full border border-neutral-200 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary/50 form-input-focus text-sm resize-none"></textarea>
                </div>
                <div class="flex justify-between items-center">
                  <div class="flex space-x-2">
                    <button
                      class="flex items-center space-x-1 text-primary/70 hover:text-primary transition-custom px-3 py-1 rounded-full text-sm">
                      <i class="fa-solid fa-image"></i>
                      <span>添加图片</span>
                    </button>
                    <button
                      class="flex items-center space-x-1 text-primary/70 hover:text-primary transition-custom px-3 py-1 rounded-full text-sm">
                      <i class="fa-solid fa-face-smile"></i>
                      <span>添加表情</span>
                    </button>
                  </div>
                  <button
                    class="px-5 py-2 rounded-full bg-gradient-love text-white hover:opacity-90 transition-custom shadow-md hover:shadow-lg text-sm font-medium">
                    发布日记
                  </button>
                </div>
              </div>
            </div>

            <!-- 日记列表 -->
            <div class="space-y-6 mt-6">
              <!-- 日记1 -->
              <div class="bg-white rounded-xl shadow-lg overflow-hidden post-card" v-for="diary in diaries"
                :key="diary.id">
                <div class="p-6">
                  <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-3">
                      <div class="w-10 h-10 rounded-full overflow-hidden">
                        <img :src="diary.author === myName ? userAvatar : partnerAvatar" alt="作者头像"
                          class="w-full h-full object-cover">
                      </div>
                      <div>
                        <h4 class="font-semibold text-neutral-900">{{ diary.author }}</h4>
                        <p class="text-neutral-500 text-xs">{{ diary.date }}</p>
                      </div>
                    </div>
                    <div class="text-xs text-primary">
                      {{ diary.weather }}
                    </div>
                  </div>
                  <h3 class="text-lg font-semibold text-neutral-900 mb-3">{{ diary.title }}</h3>
                  <div class="text-neutral-700 mb-4 whitespace-pre-line">{{ diary.content }}</div>
                  <div v-if="diary.images && diary.images.length > 0" class="grid grid-cols-2 gap-2 mb-4">
                    <img v-for="(img, index) in diary.images" :key="index" :src="img" alt="日记图片"
                      class="rounded-lg w-full h-40 object-cover hover-scale">
                  </div>
                  <div class="flex justify-between items-center">
                    <div class="flex space-x-4">
                      <button class="flex items-center space-x-1 text-neutral-500 hover:text-primary transition-custom">
                        <i class="fa-regular fa-heart"></i>
                        <span>{{ diary.likes }}</span>
                      </button>
                      <button class="flex items-center space-x-1 text-neutral-500 hover:text-primary transition-custom">
                        <i class="fa-regular fa-comment"></i>
                        <span>{{ diary.commentsCount }}</span>
                      </button>
                    </div>
                    <button class="text-neutral-500 hover:text-primary transition-custom">
                      <i class="fa-solid fa-ellipsis-h"></i>
                    </button>
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
  name: 'LoveSync',
  data () {
    return {
      userAvatar: 'https://picsum.photos/200/200?random=1',
      myName: '小甜甜',
      partnerAvatar: 'https://picsum.photos/200/200?random=2',
      partnerName: '小帅帅',
      loveDays: 365,
      totalDiaries: 128,
      myDiaries: 70,
      partnerDiaries: 58,
      diaries: [
        {
          id: 1,
          author: '小甜甜',
          date: '今天 14:30',
          weather: '☀️ 晴天',
          title: '一周年纪念',
          content: '今天是我们恋爱一周年的日子！我们一起去了第一次约会的餐厅，回忆起了很多美好的瞬间。虽然一年过得很快，但每一天都充满了爱和幸福。谢谢你，我的宝贝！💕',
          images: [
            'https://picsum.photos/600/400?random=40',
            'https://picsum.photos/600/400?random=41'
          ],
          likes: 24,
          commentsCount: 8
        },
        {
          id: 2,
          author: '小帅帅',
          date: '昨天 20:15',
          weather: '🌙 夜晚',
          title: '一起做饭',
          content: '今天和宝贝一起做了晚餐，虽然过程有些手忙脚乱，但结果很完美！她负责洗菜切菜，我负责炒菜，配合得越来越默契了。吃完饭后我们一起看了电影，度过了一个温馨的夜晚。❤️',
          images: [
            'https://picsum.photos/600/400?random=50'
          ],
          likes: 18,
          commentsCount: 5
        },
        {
          id: 3,
          author: '小甜甜',
          date: '3天前 16:45',
          weather: '🌧️ 雨天',
          title: '雨中漫步',
          content: '今天下雨了，我们打着伞一起在雨中漫步。虽然衣服被淋湿了一些，但我们都很开心。雨滴打在伞上的声音，还有我们的笑声，构成了最美的旋律。我喜欢和你一起度过的每一个瞬间！💕',
          likes: 32,
          commentsCount: 12
        }
      ]
    }
  }
}
</script>
