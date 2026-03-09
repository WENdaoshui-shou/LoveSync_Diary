<template>
  <div id="app">
    <transition name="fade" mode="out-in">
      <div key="$route.path" class="page-container">
        <!-- 背景图片 -->
        <div class="background-image"></div>
        <!-- 页面内容 -->
        <router-view />
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100%;
}

html,
body {
  height: 100%;
  margin: 0;
  padding: 0;
}

* {
  box-sizing: border-box;
}

/* 页面容器 */
.page-container {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

/* 背景图片 */
.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: "{static/images/background.jpg}";
  background-size: cover;
  background-position: center;
  opacity: 0.3;
  z-index: -1;
  transition: opacity 0.5s ease, transform 0.5s ease;
}

/* 页面切换过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* 背景图片动画 */
.fade-enter-from .background-image,
.fade-leave-to .background-image {
  opacity: 0;
  transform: scale(1.1);
}
</style>