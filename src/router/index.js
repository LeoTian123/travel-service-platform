import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import TourismRecommendation from '../views/TourismRecommendation.vue'
import MyDiary from '../views/MyDiary.vue' // 引入旅游日记页面
import AllDiaries from '../views/AllDiaries.vue' // 引入所有日记页面
import CreateDiary from '@/views/CreateDiary.vue'
import ShowMap from '@/views/ShowMap.vue' // 确保路径正确
import DiaryDetail from '@/views/DiaryDetail.vue' // 引入旅游日记详情页面
// 删除 SpotDetail 的导入
// import SpotDetail from '@/views/SpotDetail.vue' 
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/tourism-recommendation', // 所有景点
    name: 'TourismRecommendation',
    component: TourismRecommendation
  },
  {
    path: '/my-diary', // 个人主页
    name: 'MyDiary',
    component: MyDiary
  },
  {
    path: '/all-diaries', // 所有日记
    name: 'AllDiaries',
    component: AllDiaries
  },
  {
    path: '/recommended-spots', // 猜你想去
    name: 'RecommendedSpots',
    component: () => import('@/views/RecommendedSpots.vue')
  },
  {
    path: '/create-diary', // 发布日记
    name: 'CreateDiary',
    component: CreateDiary
  },
  {
    path: '/diary-detail/:id', // 日记详情
    name: 'DiaryDetail',
    component: DiaryDetail,
    props: true
  },
  {
    path: '/show-map',  // 地图
    name: 'ShowMap',
    component: () => import('@/views/ShowMap.vue'),
    props: (route) => ({ id: route.query.id }) // 传递 query 参数
  },
  {
    path: '/',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router