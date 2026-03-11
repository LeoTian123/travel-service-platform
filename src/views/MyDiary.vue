<template>
  <div class="diary-container">
    <!-- 侧边导航栏 -->
    <Sidebar v-if="hasSidebar" />

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 用户信息卡片简化版 -->
      <div class="user-profile-card">
        <h1 class="username">用户名：{{ currentUser.name }}</h1>
      </div>

      <!-- 标签导航 -->
      <el-tabs v-model="activeTab" class="nav-tabs">
        <!-- 我的日记标签页 -->
        <el-tab-pane name="notes">
          <template #label>
            <span class="tab-label">
              <el-icon><Notebook /></el-icon>
              我发布的日记
            </span>
          </template>
          
          <!-- 日记列表 -->
          <div v-if="diaries.length > 0" class="card-container">
            <DiaryCard
              v-for="diary in diaries"
              :key="diary.journal_id"
              :diary="diary"
              :show-author="false"
              @click="handleViewDetail(diary.journal_id)"
              @like="handleLike"
            />
          </div>
          <div v-else class="empty-state">
            <el-empty description="暂无日记" />
          </div>

          <!-- 日记分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[12, 24, 36, 48]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-tab-pane>

        <!-- 我的点赞标签页 -->
        <el-tab-pane name="likes">
          <template #label>
            <span class="tab-label">
              <el-icon><StarFilled /></el-icon>
              我喜欢的景点
            </span>
          </template>
          
          <!-- 景点列表 -->
          <div v-if="likedSpots.length > 0" class="card-container">
            <SpotCard
              v-for="spot in likedSpots"
              :key="spot.id"
              :spot="spot"
              @view-map="handleViewMap"
              @view-diaries="handleViewDiaries"
              @like="handleLike"
            />
          </div>
          <div v-else class="empty-state">
            <el-empty description="暂无点赞内容" />
          </div>

          <!-- 景点分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="likesCurrentPage"
              v-model:page-size="likesPageSize"
              :page-sizes="[12, 24, 36, 48]"
              :total="likesTotal"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleLikesSizeChange"
              @current-change="handleLikesCurrentChange"
            />
          </div>
        </el-tab-pane>

        <!-- 我喜欢的日记标签页 -->
        <el-tab-pane name="likedJournals">
          <template #label>
            <span class="tab-label">
              <el-icon><StarFilled /></el-icon>
              我喜欢的日记
            </span>
          </template>
          
          <!-- 喜欢的日记列表 -->
          <div v-if="likedJournals.length > 0" class="card-container">
            <DiaryCard
              v-for="diary in likedJournals"
              :key="diary.journal_id"
              :diary="diary"
              :show-author="true"
              @click="handleViewDetail(diary.journal_id)"
              @like="handleLike"
            />
          </div>
          <div v-else class="empty-state">
            <el-empty description="暂无喜欢的日记" />
          </div>

          <!-- 喜欢的日记分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="likedJournalsCurrentPage"
              v-model:page-size="likedJournalsPageSize"
              :page-sizes="[12, 24, 36, 48]"
              :total="likedJournalsTotal"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleLikedJournalsSizeChange"
              @current-change="handleLikedJournalsCurrentChange"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Location, Notebook, Star, StarFilled, 
  View, ChatDotRound, Edit 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import Sidebar from '@/components/Sidebar.vue'
import DiaryCard from '@/components/cards/DiaryCard.vue'
import SpotCard from '@/components/cards/SpotCard.vue'
import { 
  getJournalsList, 
  likeJournal, 
  unlikeJournal, 
  getImageUrl,
  getUserLikedJournals
} from '@/api/journals'
import { getUserLikedAttractions, likeAttraction, unlikeAttraction } from '@/api/attractions'

// 响应式数据
const activeTab = ref('notes')
const hasSidebar = ref(true)
const router = useRouter()
const diaries = ref([])
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

// 用户信息
const user = JSON.parse(localStorage.getItem('user'))
const currentUser = computed(() => ({
  name: user?.username || '未命名用户'
}))

// 日记相关方法
const fetchDiaries = async () => {
  try {
    const params = {
      page_num: currentPage.value - 1,
      page_size: pageSize.value,
      user_id: user?.id,
      uploader_id: user?.id,
      sort_type: 'date',
      sort_direction: 'desc'
    }

    const response = await getJournalsList(params)
    
    if (response.data?.ret === 0) {
      const responseData = response.data.data
      diaries.value = responseData.retlist
      total.value = responseData.page_size * responseData.total_pages
      currentPage.value = responseData.current_page + 1
    } else {
      ElMessage.error('获取日记数据失败')
      diaries.value = []
    }
  } catch (error) {
    console.error('获取日记数据失败:', error)
    ElMessage.error('获取日记数据失败，请稍后重试')
    diaries.value = []
  }
}

// 景点相关数据
const likedSpots = ref([])
const likesCurrentPage = ref(1)
const likesPageSize = ref(12)
const likesTotal = ref(0)
const defaultImage = ref('/images/default-spot.jpg')

const fetchLikedSpots = async () => {
  try {
    const params = {
      page_num: likesCurrentPage.value - 1,
      page_size: likesPageSize.value,
      user_id: user?.id
    }

    const response = await getUserLikedAttractions(params)
    
    if (response.data?.ret === 0) {
      const responseData = response.data.data
      likedSpots.value = responseData.retlist.map(item => ({
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
      likesTotal.value = responseData.page_size * responseData.total_pages
      likesCurrentPage.value = responseData.current_page + 1
    } else {
      ElMessage.error(response.data.msg || '获取点赞景点数据失败')
      likedSpots.value = []
    }
  } catch (error) {
    console.error('获取点赞景点数据失败:', error)
    ElMessage.error('获取点赞景点数据失败，请稍后重试')
    likedSpots.value = []
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

// 处理喜欢/点赞
const handleLike = async (item) => {
  try {
    if (!user) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }
    
    const userId = user.id
    
    if ('journal_id' in item) {
      // 日记点赞
      const action = item.is_liked ? unlikeJournal : likeJournal
      const response = await action(userId, item.journal_id)
      
      if (response.data.status === 'success') {
        item.num_likes = response.data.likes_count
        item.is_liked = !item.is_liked
        ElMessage.success(item.is_liked ? '日记点赞成功' : '已取消日记点赞')
      }
    } else {
      // 景点点赞
      const action = item.isLiked ? unlikeAttraction : likeAttraction
      const response = await action(userId, item.id)
      
      if (response.data.status === 'success') {
        item.likes = response.data.likes_count
        item.isLiked = !item.isLiked
        ElMessage.success(item.isLiked ? '景点点赞成功' : '已取消景点点赞')
      }
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

// 喜欢的日记相关数据
const likedJournals = ref([])
const likedJournalsCurrentPage = ref(1)
const likedJournalsPageSize = ref(12)
const likedJournalsTotal = ref(0)

const fetchLikedJournals = async () => {
  try {
    const params = {
      page_num: likedJournalsCurrentPage.value - 1,
      page_size: likedJournalsPageSize.value,
      user_id: user?.id
    }

    const response = await getUserLikedJournals(params)
    
    if (response.data?.ret === 0) {
      const responseData = response.data.data
      likedJournals.value = responseData.retlist
      likedJournalsTotal.value = responseData.page_size * responseData.total_pages
      likedJournalsCurrentPage.value = responseData.current_page + 1
    } else {
      ElMessage.error(response.data.msg || '获取喜欢的日记数据失败')
      likedJournals.value = []
    }
  } catch (error) {
    console.error('获取喜欢的日记数据失败:', error)
    ElMessage.error('获取喜欢的日记数据失败，请稍后重试')
    likedJournals.value = []
  }
}

// 分页处理方法
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchDiaries()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchDiaries()
}

const handleLikesSizeChange = (val) => {
  likesPageSize.value = val
  likesCurrentPage.value = 1
  fetchLikedSpots()
}

const handleLikesCurrentChange = (val) => {
  likesCurrentPage.value = val
  fetchLikedSpots()
}

const handleLikedJournalsSizeChange = (val) => {
  likedJournalsPageSize.value = val
  likedJournalsCurrentPage.value = 1
  fetchLikedJournals()
}

const handleLikedJournalsCurrentChange = (val) => {
  likedJournalsCurrentPage.value = val
  fetchLikedJournals()
}

// 查看日记详情
const handleViewDetail = (id) => {
  window.open(`/diary-detail/${id}`, '_blank')
}

// 初始化数据
onMounted(() => {
  if (!user) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  fetchDiaries()
  fetchLikedSpots()
  fetchLikedJournals()
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

.diary-container {
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

.user-profile-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  margin-bottom: 30px;
  text-align: center;
  width: 100%;
  max-width: 1200px;

  .username {
    font-size: 28px;
    font-weight: 600;
    margin: 0;
    color: #303133;
  }
}

.nav-tabs {
  width: 100%;
  max-width: 1200px;
  
  :deep(.el-tabs__nav-wrap) {
    padding: 0 20px;
    display: flex;
    justify-content: flex-start;
  }
  
  :deep(.el-tabs__nav-scroll) {
    display: flex;
    justify-content: flex-start;
  }
  
  :deep(.el-tabs__nav) {
    float: none;
    display: inline-flex;
  }
  
  :deep(.el-tabs__header) {
    margin: 0 0 2rem 0;
    text-align: left;
  }

  :deep(.el-tabs__item) {
    font-size: 1rem;
    padding: 0 24px;
    height: 48px;
    display: flex;
    align-items: center;

    .tab-label {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
}

.card-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  width: 100%;
  padding: 0 20px;
}

.empty-state {
  padding: 3rem 0;
  text-align: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.pagination-container {
  margin-top: 30px;
  padding: 20px 0;
  display: flex;
  justify-content: center;
  width: 100%;
}
</style>