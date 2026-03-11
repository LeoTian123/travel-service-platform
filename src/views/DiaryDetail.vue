<template>
  <div class="diary-container">
    <!-- 只有当有图片时才显示轮播图 -->
    <el-carousel 
      v-if="images && images.length > 0"
      indicator-position="outside"
      height="600px"
      class="carousel-container"
    >
      <el-carousel-item v-for="(img, index) in images" :key="index">
        <div class="image-container">
          <img :src="getImageUrl(img)" class="carousel-image" />
        </div>
      </el-carousel-item>
    </el-carousel>

    <!-- 主要内容区域 -->
    <div class="content-container">
      <!-- 用户信息区 -->
      <div class="user-info-card">
        <div class="user-meta">
          <h3 class="username">{{ diary.user_name }}</h3>
          <span class="post-time">{{ diary.date }}</span>
        </div>
      </div>

      <!-- 标题和景点 -->
      <h1 class="diary-title">{{ diary.title }}</h1>
      <div class="spot-tag">
        <el-tag type="info" effect="plain" round>
          <el-icon><Location /></el-icon>
          {{ diary.spot_name }}
        </el-tag>
      </div>

      <!-- 正文内容 -->
      <article class="diary-content">
        <p class="content-paragraph">{{ diary.content }}</p>
      </article>

      <!-- 互动操作区 -->
      <div class="action-bar">
        <div class="action-item">
          <el-button
            :type="diary.is_liked ? 'danger' : 'warning'"
            size="small"
            @click="handleLike"
          >
            <el-icon><StarFilled /></el-icon>
            {{ diary.num_likes }} {{ diary.is_liked ? '已喜欢' : '喜欢' }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Location, StarFilled } from '@element-plus/icons-vue'
import { getJournalDetail, getImageUrl, likeJournal, unlikeJournal } from '@/api/journals'

const route = useRoute()
const router = useRouter()
const diary = ref({})
const images = ref([])

// 获取用户信息
const user = JSON.parse(localStorage.getItem('user'))

// 获取日记详情
const fetchDiaryDetail = async () => {
  try {
    const response = await getJournalDetail(route.params.id, user?.id)
    if (response.data && response.data.ret === 0) {
      diary.value = response.data.journal
      images.value = response.data.journal.imgs || []
    } else {
      ElMessage.error('获取日记详情失败')
    }
  } catch (error) {
    console.error('获取日记详情失败:', error)
    ElMessage.error('获取日记详情失败，请稍后重试')
  }
}

// 处理点赞
const handleLike = async () => {
  try {
    if (!user) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }
    
    const action = diary.value.is_liked ? unlikeJournal : likeJournal
    const response = await action(user.id, diary.value.journal_id)
    
    if (response.data.status === 'success') {
      diary.value.num_likes = response.data.likes_count
      diary.value.is_liked = !diary.value.is_liked
      ElMessage.success(diary.value.is_liked ? '点赞成功' : '已取消点赞')
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

onMounted(() => {
  if (!user) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  fetchDiaryDetail()
})
</script>

<style scoped lang="scss">
.diary-container {
  max-width: 800px;
  margin: 0px auto;
  padding: 24px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.08);
}

.carousel-container {
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 32px;
  
  .image-container {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #f5f5f5;
  }

  .carousel-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }
}

.user-info-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 24px;

  .user-meta {
    flex: 1;
    
    .username {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: #333;
    }

    .post-time {
      color: #666;
      font-size: 12px;
      margin-top: 4px;
    }
  }
}

.diary-title {
  font-size: 32px;
  line-height: 1.3;
  margin: 0 0 20px;
  color: #1a1a1a;
}

.spot-tag {
  margin-bottom: 24px;
}

.diary-content {
  color: #333;
  line-height: 1.8;
  margin-bottom: 32px;

  .content-paragraph {
    margin: 18px 0;
    font-size: 15px;
  }
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  padding: 24px 0;
  margin: 32px 0;
  border-top: 1px solid #eee;
}
</style>