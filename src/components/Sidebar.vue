<!-- filepath: /Users/mr.hu/Desktop/学习相关文件/大二下/数据结构课设/demo/src/components/Sidebar.vue -->
<template>
    <div class="sidebar">
      <h2 class="sidebar-title">导航栏</h2>
      <ul class="sidebar-menu">
        <li>
          <router-link to="/tourism-recommendation" class="sidebar-link">
            <el-icon><Location /></el-icon>
            <span>旅游推荐</span>
          </router-link>
        </li>
        <li>
          <router-link to="/recommended-spots" class="sidebar-link">
            <el-icon><Star /></el-icon>
            <span>猜你想去</span>
          </router-link>
        </li>
        <li>
          <router-link to="/all-diaries" class="sidebar-link">
            <el-icon><Collection /></el-icon>
            <span>所有日记</span>
          </router-link>
        </li>
        <li>
          <router-link to="/create-diary" class="sidebar-link" target="_blank">
            <el-icon><Collection /></el-icon>
            <span>发布日记</span>
          </router-link>
        </li>
        <li>
          <router-link to="/my-diary" class="sidebar-link">
            <el-icon><Notebook /></el-icon>
            <span>我的主页</span>
          </router-link>
        </li>
        <!-- 退出登录按钮 -->
        <li>
          <el-button class="logout-button" type="danger" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-button>
        </li>
      </ul>
    </div>
  </template>

  <script setup>
  import { Location, Notebook, SwitchButton, Collection } from '@element-plus/icons-vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'

  const router = useRouter()

  // 退出登录
  const handleLogout = () => {
    localStorage.removeItem('token')
    ElMessage.success('退出登录成功！')
    router.push('/login')
  }
  </script>

  <style scoped>
  .sidebar {
    width: 16%; /* 占据页面 1/6 宽度 */
    background-color: #f5f5f5; /* 背景颜色 */
    padding: 20px; /* 内边距 */
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1); /* 阴影效果 */
    position: fixed; /* 固定定位 */
    top: 0; /* 顶部对齐 */
    left: 0; /* 左侧对齐 */
    bottom: 0; /* 底部对齐 */
  }

  .sidebar-title {
    font-size: 18px; /* 字体大小 */
    margin-bottom: 20px; /* 底部外边距 */
  }

  .sidebar-menu {
    list-style: none; /* 去掉列表样式 */
    padding: 0; /* 去掉内边距 */
  }

  .sidebar-menu li {
    margin-bottom: 10px; /* 底部外边距 */
  }

  .sidebar-link {
    display: flex; /* 使用 flex 布局 */
    align-items: center; /* 垂直居中 */
    text-decoration: none; /* 去掉下划线 */
    color: #2c3e50; /* 字体颜色 */
    padding: 10px; /* 内边距 */
    border-radius: 4px; /* 圆角 */
    transition: background-color 0.3s; /* 背景颜色过渡效果 */
  }

  .sidebar-link:hover {
    background-color: #e0e0e0; /* 鼠标悬停时的背景色 */
  }

  .sidebar-link .el-icon {
    margin-right: 10px; /* 右侧外边距 */
  }

  .logout-button {
    width: 100%; /* 宽度占满父容器 */
    margin-top: 20px; /* 顶部外边距 */
    background-color: #ff4d4f; /* 背景颜色 */
    border: none; /* 去掉边框 */
    color: white; /* 字体颜色 */
    display: flex; /* 使用 flex 布局 */
    align-items: center; /* 垂直居中 */
    justify-content: center; /* 水平居中 */
  }

  .logout-button:hover {
    background-color: #ff7875; /* 鼠标悬停时的背景色 */
  }
  </style>