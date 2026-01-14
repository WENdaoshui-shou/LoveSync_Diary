<template>
  <div
    class="font-inter bg-neutral-100 text-neutral-800 min-h-screen flex flex-col overflow-x-hidden relative scroll-smooth">
    <!-- 背景装饰元素 -->
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -left-40 w-80 h-80 bg-primary/10 rounded-full filter blur-3xl float-animation"></div>
      <div class="absolute -bottom-20 -right-20 w-80 h-80 bg-secondary/10 rounded-full filter blur-3xl float-animation"
        style="animation-delay: -2s;"></div>
      <div class="absolute top-1/3 right-1/4 w-40 h-40 bg-primary/5 rounded-full filter blur-2xl float-animation"
        style="animation-delay: -4s;"></div>
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
            class="text-neutral-700 hover:text-primary transition-custom font-medium px-1 py-2 border-b-2 border-transparent hover:border-primary">双人日记</router-link>

          <!-- 更多下拉菜单 -->
          <div class="relative" id="moreDropdown">
            <button
              class="text-neutral-700 hover:text-primary transition-custom font-medium flex items-center px-1 py-2"
              id="moreButton">
              更多 <i class="fa-solid fa-chevron-down ml-1 text-xs"></i>
            </button>
            <div class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl py-2 z-50 hidden" id="moreOptions">
              <router-link to="/couple"
                class="block px-4 py-2 text-neutral-700 hover:bg-neutral-50 transition-custom flex items-center">
                <i class="fa-solid fa-calendar-heart mr-2 w-5 text-center"></i>情侣设置
              </router-link>
              <router-link to="/couple-recommendation"
                class="block px-4 py-2 text-neutral-700 hover:bg-neutral-50 transition-custom flex items-center">
                <i class="fa-solid fa-gift mr-2 w-5 text-center"></i>情侣推荐
              </router-link>
              <router-link to="/couple-places"
                class="block px-4 py-2 text-neutral-700 hover:bg-neutral-50 transition-custom flex items-center">
                <i class="fa-solid fa-map-marker-heart mr-2 w-5 text-center"></i>情侣地点
              </router-link>
              <router-link to="/couple-test"
                class="block px-4 py-2 text-neutral-700 hover:bg-neutral-50 transition-custom flex items-center">
                <i class="fa-solid fa-question-circle mr-2 w-5 text-center"></i>爱情测试
              </router-link>
            </div>
          </div>
        </nav>

        <!-- 内容过滤器 -->
        <div
          class="bg-white/95 backdrop-blur-md rounded-xl shadow-lg p-2 flex justify-between items-center hover-scale">
          <div class="flex space-x-2">
            <button class="px-4 py-2 rounded-full bg-primary text-white text-sm font-medium">推荐</button>
            <button
              class="px-4 py-2 rounded-full bg-neutral-100 text-neutral-700 text-sm font-medium hover:bg-neutral-200 transition-custom">最新</button>
            <button
              class="px-4 py-2 rounded-full bg-neutral-100 text-neutral-700 text-sm font-medium hover:bg-neutral-200 transition-custom">热门</button>
          </div>
          <div class="relative">
            <input type="text" placeholder="LoveSync: 搜索..."
              class="pl-10 pr-4 py-2 rounded-full border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-primary/50 form-input-focus text-sm">
            <i class="fa-solid fa-search absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400"></i>
          </div>
        </div>

        <!-- 用户操作区 -->
        <div class="flex items-center space-x-4">
          <router-link to="/moments" id="createPostLink"
            class="hidden md:flex items-center space-x-2 px-5 py-2 rounded-full bg-gradient-love text-white hover:opacity-90 transition-custom shadow-md hover:shadow-lg">
            <i class="fa-solid fa-pencil"></i>
            <span>发布动态</span>
          </router-link>

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

          <!-- 移动端菜单按钮 -->
          <button class="md:hidden text-neutral-700 focus:outline-none" id="menu-toggle">
            <i class="fa-solid fa-bars text-xl"></i>
          </button>
        </div>
      </div>

      <!-- 移动端菜单 -->
      <div id="mobile-menu"
        class="hidden md:hidden bg-white shadow-lg absolute w-full transform -translate-y-2 opacity-0 transition-all duration-200 ease-in-out"
        style="top: 100%;">
        <div class="container mx-auto px-4 py-3 flex flex-col space-y-3">
          <router-link to="/community"
            class="text-neutral-700 hover:text-primary py-2 transition-custom font-medium flex items-center">
            <i class="fa-solid fa-users mr-3 w-5 text-center"></i>爱享公社
          </router-link>
          <router-link to="/moments"
            class="text-neutral-700 hover:text-primary py-2 transition-custom font-medium flex items-center">
            <i class="fa-solid fa-bolt mr-3 w-5 text-center"></i>心动轨迹
          </router-link>
          <router-link to="/photo-album"
            class="text-neutral-700 hover:text-primary py-2 transition-custom font-medium flex items-center">
            <i class="fa-solid fa-images mr-3 w-5 text-center"></i>心跳相簿
          </router-link>
          <router-link to="/lovesync"
            class="text-neutral-700 hover:text-primary py-2 transition-custom font-medium flex items-center">
            <i class="fa-solid fa-bookmark mr-3 w-5 text-center"></i>双人日记
          </router-link>
          <div class="border-t border-neutral-200 my-1"></div>
          <a href="#" class="text-neutral-700 py-2 transition-custom flex items-center">
            <i class="fa-solid fa-calendar-heart mr-3 w-5 text-center"></i>纪念日提醒
          </a>
          <a href="#" class="text-neutral-700 py-2 transition-custom flex items-center">
            <i class="fa-solid fa-gift mr-3 w-5 text-center"></i>礼物推荐
          </a>
          <a href="#" class="text-neutral-700 py-2 transition-custom flex items-center">
            <i class="fa-solid fa-map-marker-heart mr-3 w-5 text-center"></i>情侣地点
          </a>
          <a href="#" class="text-neutral-700 py-2 transition-custom flex items-center">
            <i class="fa-solid fa-question-circle mr-3 w-5 text-center"></i>爱情测试
          </a>
          <div class="border-t border-neutral-200 my-1"></div>
          <router-link to="/personal-center" class="text-neutral-700 py-2 transition-custom flex items-center">
            <i class="fa-solid fa-user mr-3 w-5 text-center"></i>主页
          </router-link>
          <router-link to="/message" class="text-neutral-700 py-2 transition-custom flex items-center">
            <i class="fa-solid fa-bookmark mr-3 w-5 text-center"></i>消息
          </router-link>
          <router-link to="/settings" class="text-neutral-700 py-2 transition-custom flex items-center">
            <i class="fa-solid fa-cog mr-3 w-5 text-center"></i>设置
          </router-link>
          <div class="border-t border-neutral-200 my-1"></div>
          <a href="#" @click="logout" class="text-red-500 py-2 transition-custom flex items-center">
            <i class="fa-solid fa-sign-out mr-3 w-5 text-center"></i>退出登录
          </a>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="flex-grow pt-24 pb-16 relative z-10">
      <div class="container mx-auto px-4 space-y-6">
        <!-- 个人信息展示 -->
        <div class="bg-white rounded-xl shadow-lg overflow-hidden hover-scale">
          <div class="h-32 bg-gradient-love relative">
            <div class="absolute -bottom-8 left-6 w-16 h-16 rounded-full border-4 border-white overflow-hidden">
              <img :src="userAvatar" alt="用户头像" class="w-full h-full object-cover">
            </div>
          </div>
          <div class="pt-10 pb-6 px-6">
            <h3 class="text-lg font-semibold text-neutral-900">{{ userName }}</h3>
            <p class="text-neutral-600 text-sm mt-1">分享我们的爱情故事</p>
            <div class="flex justify-between mt-4 pt-4 border-t border-neutral-200">
              <div class="text-center">
                <p class="text-neutral-900 font-semibold">{{ momentsCount }}</p>
                <p class="text-neutral-500 text-xs">动态</p>
              </div>
              <div class="text-center">
                <p class="text-neutral-900 font-semibold">128</p>
                <p class="text-neutral-500 text-xs">粉丝</p>
              </div>
              <div class="text-center">
                <p class="text-neutral-900 font-semibold">64</p>
                <p class="text-neutral-500 text-xs">关注</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 爱情誓言 -->
        <div class="bg-white rounded-xl shadow-lg p-6 hover-scale relative overflow-hidden">
          <div class="absolute top-0 right-0 w-20 h-20 bg-primary/10 rounded-full -mr-10 -mt-10"></div>
          <div class="absolute bottom-0 left-0 w-16 h-16 bg-secondary/10 rounded-full -ml-8 -mb-8"></div>
          <h3 class="text-lg font-semibold text-neutral-900 mb-4">爱情誓言</h3>
          <p class="text-neutral-700 italic relative z-10">"{{ userBio }}"</p>
          <div class="flex justify-between mt-4">
            <span class="text-sm text-neutral-500">{{ userName }}</span>
            <span class="text-sm text-neutral-500">{{ coupleName || '无伴侣' }}</span>
          </div>
        </div>

        <!-- 爱情故事时间轴 -->
        <div class="bg-white rounded-xl shadow-lg p-6 hover-scale">
          <h3 class="text-lg font-semibold text-neutral-900 mb-6">爱情故事时间轴</h3>
          <div class="relative">
            <div class="timeline-line"></div>

            <!-- 时间点1 -->
            <div class="relative pb-12">
              <div class="timeline-dot" style="top: 0;"></div>
              <div class="flex justify-between items-center">
                <div class="w-5/12 text-right pr-8">
                  <span class="text-xs text-primary font-medium">2022年3月15日</span>
                  <h4 class="text-neutral-900 font-semibold mt-1">第一次相遇</h4>
                  <p class="text-neutral-600 text-sm mt-1">在朋友的生日派对上，我们第一次见面，一见钟情。</p>
                </div>
                <div class="w-2/12"></div>
                <div class="w-5/12 pl-8">
                  <div class="rounded-lg overflow-hidden hover-scale">
                    <img src="https://picsum.photos/400/300?random=40" alt="第一次相遇" class="w-full h-32 object-cover">
                  </div>
                </div>
              </div>
            </div>

            <!-- 时间点2 -->
            <div class="relative pb-12">
              <div class="timeline-dot" style="top: 0;"></div>
              <div class="flex justify-between items-center">
                <div class="w-5/12 text-right pr-8">
                  <div class="rounded-lg overflow-hidden hover-scale">
                    <img src="https://picsum.photos/400/300?random=41" alt="第一次约会" class="w-full h-32 object-cover">
                  </div>
                </div>
                <div class="w-2/12"></div>
                <div class="w-5/12 pl-8">
                  <span class="text-xs text-primary font-medium">2022年4月20日</span>
                  <h4 class="text-neutral-900 font-semibold mt-1">第一次约会</h4>
                  <p class="text-neutral-600 text-sm mt-1">我们一起去看了电影，吃了晚餐，度过了一个美好的夜晚。</p>
                </div>
              </div>
            </div>

            <!-- 时间点3 -->
            <div class="relative">
              <div class="timeline-dot" style="top: 0;"></div>
              <div class="flex justify-between items-center">
                <div class="w-5/12 text-right pr-8">
                  <span class="text-xs text-primary font-medium">2022年5月28日</span>
                  <h4 class="text-neutral-900 font-semibold mt-1">确定关系</h4>
                  <p class="text-neutral-600 text-sm mt-1">在美丽的夕阳下，我向她表白，她答应成为我的女朋友。</p>
                </div>
                <div class="w-2/12"></div>
                <div class="w-5/12 pl-8">
                  <div class="rounded-lg overflow-hidden hover-scale">
                    <img src="https://picsum.photos/400/300?random=42" alt="确定关系" class="w-full h-32 object-cover">
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 音乐播放器 -->
        <div class="bg-white rounded-xl shadow-lg p-6 hover-scale">
          <h3 class="text-lg font-semibold text-neutral-900 mb-4">我们的歌单</h3>
          <div class="flex items-center space-x-4">
            <div class="w-16 h-16 rounded-lg overflow-hidden">
              <img src="https://picsum.photos/100/100?random=50" alt="音乐封面" class="w-full h-full object-cover">
            </div>
            <div class="flex-1">
              <h4 class="text-neutral-900 font-medium">我们的主题曲</h4>
              <p class="text-neutral-500 text-sm">《Love Story》 - Taylor Swift</p>
            </div>
            <div class="flex items-center space-x-3">
              <button
                class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary hover:bg-primary hover:text-white transition-custom">
                <i class="fa-solid fa-step-backward"></i>
              </button>
              <button
                class="w-12 h-12 rounded-full bg-primary flex items-center justify-center text-white hover:opacity-90 transition-custom">
                <i class="fa-solid fa-play"></i>
              </button>
              <button
                class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary hover:bg-primary hover:text-white transition-custom">
                <i class="fa-solid fa-step-forward"></i>
              </button>
            </div>
          </div>
          <div class="mt-4">
            <div class="h-1 bg-neutral-200 rounded-full overflow-hidden">
              <div class="h-full bg-primary rounded-full" style="width: 35%"></div>
            </div>
            <div class="flex justify-between mt-2 text-xs text-neutral-500">
              <span>1:25</span>
              <span>3:58</span>
            </div>
          </div>
          <div class="mt-4 music-wave">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>

        <!-- 情侣问答模块 -->
        <div class="bg-white rounded-xl shadow-lg p-6 hover-scale">
          <h3 class="text-lg font-semibold text-neutral-900 mb-4">情侣默契大考验</h3>
          <div class="space-y-4">
            <div class="p-4 border border-neutral-200 rounded-lg hover:border-primary transition-custom">
              <h4 class="text-neutral-900 font-medium">对方最喜欢的颜色是什么？</h4>
              <div class="mt-3 grid grid-cols-2 gap-2">
                <div class="p-3 bg-neutral-50 rounded-lg flex items-center">
                  <div class="w-5 h-5 rounded-full bg-blue-500 mr-2"></div>
                  <span>蓝色</span>
                  <div class="ml-auto text-green-500 text-xs">
                    <i class="fa-solid fa-check"></i> 正确
                  </div>
                </div>
                <div class="p-3 bg-neutral-50 rounded-lg flex items-center">
                  <div class="w-5 h-5 rounded-full bg-pink-500 mr-2"></div>
                  <span>粉色</span>
                </div>
                <div class="p-3 bg-neutral-50 rounded-lg flex items-center">
                  <div class="w-5 h-5 rounded-full bg-purple-500 mr-2"></div>
                  <span>紫色</span>
                </div>
                <div class="p-3 bg-neutral-50 rounded-lg flex items-center">
                  <div class="w-5 h-5 rounded-full bg-green-500 mr-2"></div>
                  <span>绿色</span>
                </div>
              </div>
            </div>

            <div class="p-4 border border-neutral-200 rounded-lg hover:border-primary transition-custom">
              <h4 class="text-neutral-900 font-medium">你们第一次约会去了哪里？</h4>
              <div class="mt-3 space-y-2">
                <div class="p-3 bg-neutral-50 rounded-lg flex items-center">
                  <span>电影院</span>
                  <div class="ml-auto text-green-500 text-xs">
                    <i class="fa-solid fa-check"></i> 正确
                  </div>
                </div>
                <div class="p-3 bg-neutral-50 rounded-lg flex items-center">
                  <span>餐厅</span>
                </div>
                <div class="p-3 bg-neutral-50 rounded-lg flex items-center">
                  <span>公园</span>
                </div>
                <div class="p-3 bg-neutral-50 rounded-lg flex items-center">
                  <span>商场</span>
                </div>
              </div>
            </div>

            <button
              class="w-full py-3 bg-primary/10 text-primary rounded-lg hover:bg-primary hover:text-white transition-custom">
              开始新的考验
            </button>
          </div>
        </div>

        <!-- 个人动态列表 -->
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
  name: 'PersonalCenter',
  data () {
    return {
      userAvatar: 'https://picsum.photos/200/200?random=1',
      userName: '小甜甜',
      userBio: '爱你到永远',
      coupleName: '小帅帅',
      momentsCount: 25,
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
  },
  mounted () {
    // 初始化用户数据
    this.$store.dispatch('fetchUserData')
  }
}
</script>
