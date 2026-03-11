<template>
  <div class="tourism-container">
    <Sidebar />
    <div class="main-content">
      <h1 class="page-title">猜你想去</h1>

      <!-- 景点卡片列表 -->
      <div class="card-container">
        <SpotCard
          v-for="spot in spots"
          :key="spot.id"
          :spot="spot"
          @view-map="handleViewMap"
          @view-diaries="handleViewDiaries"
          @like="handleLike"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Sidebar from '@/components/Sidebar.vue'
import SpotCard from '@/components/cards/SpotCard.vue'
import { getUBCFRecommendations, likeAttraction, unlikeAttraction } from '@/api/attractions'

const router = useRouter()
const defaultImage = ref('/images/default-spot.jpg')
const spots = ref([])

// 获取用户信息
const user = JSON.parse(localStorage.getItem('user'))

// 获取推荐景点列表
const fetchSpots = async () => {
  try {
    if (!user?.id) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }

    const response = await getUBCFRecommendations(user.id)
    
    if (response.data && response.data.ret === 0) {
      spots.value = response.data.data.recommendations.map(item => ({
        id: item.id,
        name: item.cnName,
        enName: item.enName || '',
        description: item.description || '暂无描述',
        image: item.img_url,
        comments: item.num_comment_quna || 0,
        journals: item.num_journals || 0,
        likes: item.num_likes || 0,
        type: item.type || '未分类',
        isLiked: item.is_liked || false
      }))
    } else {
      ElMessage.error(response.data.msg || '获取推荐失败')
      spots.value = []
    }
  } catch (error) {
    console.error('获取推荐失败:', error)
    ElMessage.error('获取推荐失败，请稍后重试')
    spots.value = []
  }
}

// 图片加载错误处理
const handleImageError = (e) => {
  e.target.src = defaultImage.value
}

// 查看地图
const handleViewMap = (id) => {
  router.push({
    path: '/show-map',
    query: { id }
  })
}

// 查看相关日记
const handleViewDiaries = (id) => {
  router.push({
    path: '/all-diaries',
    query: { spot_id: id }
  })
}

// 处理点赞
const handleLike = async (spot) => {
  try {
    if (!user) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }
    
    const userId = user.id
    const action = spot.isLiked ? unlikeAttraction : likeAttraction
    const response = await action(userId, spot.id)
    
    if (response.data.status === 'success') {
      spot.likes = response.data.likes_count
      spot.isLiked = !spot.isLiked
      ElMessage.success(spot.isLiked ? '点赞成功' : '已取消点赞')
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

// 用户检查和数据加载
onMounted(() => {
  if (!user) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  fetchSpots()
})
</script>

<style scoped lang="scss">
@mixin text-ellipsis($lines) {
  display: -webkit-box;
  -webkit-line-clamp: $lines;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tourism-container {
  display: flex;
  height: 100vh;
  width: 100%;
}

.main-content {
  flex: 1;
  padding: 20px;
  background-color: #f5f7fa;
  margin-left: 20%;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: calc(100% - 16.666%);
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  margin: 20px 0 30px;
  color: #303133;
}

.card-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  width: 100%;
  padding: 0 20px;
}
</style>