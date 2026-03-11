<template>
    <div class="login-container">
      <div class="login-box">
        <h2 class="title">个性化旅游系统登录</h2>
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          label-width="80px"
          @keyup.enter="handleLogin"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入学号"
              clearable
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>
  
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              show-password
              clearable
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
  
          <!-- 记住我 -->
          <el-form-item>
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
          </el-form-item>
  
          <!-- 忘记密码 -->
          <el-form-item>
            <el-link type="primary" class="forgot-password">忘记密码?</el-link>
          </el-form-item>
  
          <el-form-item>
            <el-button
              type="primary"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              立即登录
            </el-button>
          </el-form-item>
  
          <div class="register-link">
            没有账号？
            <el-link type="primary" @click="handleRegister">立即注册</el-link>
          </div>
        </el-form>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive } from 'vue'
  import { User, Lock } from '@element-plus/icons-vue'
  import { ElMessage } from 'element-plus'
  import { useRouter } from 'vue-router'
  import request from '@/utils/request'

  const router = useRouter()
  const loginForm = reactive({
    username: '',
    password: ''
  })
  
  // 表单验证规则
  const loginRules = reactive({
    username: [
      { required: true, message: '请输入学号', trigger: 'blur' },
      { min: 4, max: 16, message: '长度在4到16个字符', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, max: 18, message: '长度在6到18个字符', trigger: 'blur' }
    ]
  })
  
  // 引用表单实例
  const loginFormRef = ref(null)
  const rememberMe = ref(false)
  const loading = ref(false)
  
  const handleLogin = () => {
    loginFormRef.value.validate(async valid => {
      if (!valid) return
      
      loading.value = true
      try {
        const response = await request.post('/users/login/', {
          username: loginForm.username,
          password: loginForm.password
        })
        
        const { token, user } = response.data
        // 存储用户信息和token
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))
        ElMessage.success('登录成功！')
        router.push('/tourism-recommendation')

      } catch (error) {
        console.error('登录错误:', error)
        ElMessage.error(error.response?.data?.msg || '登录失败')
      } finally {
        loading.value = false
      }
    })
  }
  
  // 注册跳转
  const handleRegister = () => {
    router.push('/Register') // 跳转到注册页面
  }
  </script>
  
  <style scoped>
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f5f5f5;
  }
  
  .login-box {
    width: 400px;
    padding: 20px;
    background-color: #fff;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
  }
  
  .title {
    text-align: center;
    margin-bottom: 20px;
  }
  
  .login-btn {
    width: 100%;
  }
  
  .register-link {
    text-align: center;
    margin-top: 10px;
  }
  </style>