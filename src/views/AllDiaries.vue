<template>
  <div class="diary-container">
    <Sidebar v-if="hasSidebar" />
    <div class="main-content">
      <h1 class="page-title">所有日记</h1>

      <!-- 筛选面板与搜索按钮 -->
      <div class="filter-search-container">
        <div class="filter-section">
          <FilterPanel
            :config="filterConfig"
            @filter-change="handleFilterChange"
            class="filter-panel-container"
          />
        </div>
        
        <div class="search-button-section">
          <!-- 添加重置按钮 -->
          <el-button
            v-if="$route.query.spot_id"
            class="reset-button"
            @click="handleReset"
          >
            <el-icon><RefreshLeft /></el-icon>
            重置筛选
          </el-button>
          <el-button
            type="primary"
            class="unified-search-button"
            @click="handleSearchButtonClick"
          >
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </div>
      </div>

      <!-- 日记卡片列表 -->
      <!-- 替换原有的卡片循环部分 -->
      <div v-if="diaries.length > 0" class="card-container">
        <DiaryCard
          v-for="diary in diaries"
          :key="diary.journal_id"
          :diary="diary"
          @click="handleViewDetail(diary.journal_id)"
          @like="handleLike"
        />
      </div>
      <div v-else class="empty-state">
        <el-empty description="暂无日记" />
      </div>

      <!-- 分页组件 -->
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'  // 添加 useRoute
import { RefreshLeft } from '@element-plus/icons-vue'  // 添加图标
import { ElMessage } from 'element-plus'
import {
  Location, StarFilled, Search
} from '@element-plus/icons-vue'
import Sidebar from '@/components/Sidebar.vue'
import FilterPanel from '@/components/FilterPanel.vue'
import DiaryCard from '@/components/cards/DiaryCard.vue'

// 响应式数据
const hasSidebar = ref(true)
const router = useRouter()
const route = useRoute()
const diaries = ref([])
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

// 获取用户信息
const user = JSON.parse(localStorage.getItem('user'))

// 筛选配置
const filterConfig = reactive({
  search: { placeholder: '搜索日记标题' },
  selects: {
    sortType: {
      label: '排序方式',
      placeholder: '选择排序方式',
      options: [
        { label: '默认/所有', value: 'default' },
        { label: '按喜欢数', value: 'likes' },
        { label: '按时间', value: 'date' }
      ]
    },
    sortDirection: {
      label: '排序方向',
      placeholder: '选择排序方向',
      options: [
        { label: '默认方向/从高到低/从新到旧', value: 'default' },
        { label: '倒序方向/从低到高/从旧到新', value: 'rev' }
      ]
    }
  }
})

// 当前筛选条件
const currentFilters = ref({
  search: '',
  selects: {
    sortType: 'likes',
    sortDirection: 'asc'
  }
})

// 添加搜索按钮处理函数
const handleSearchButtonClick = () => {
  fetchDiaries()
}

// 修改导入部分
import { getJournalsList, likeJournal, unlikeJournal, getImageUrl } from '@/api/journals'

// 修改获取日记列表函数
const fetchDiaries = async () => {
  try {
    const params = {
      page_num: currentPage.value - 1,
      page_size: pageSize.value,
      user_id: user?.id,
      keyword: currentFilters.value.search || undefined,
      sort_type: currentFilters.value.selects.sortType !== 'default' ? currentFilters.value.selects.sortType : undefined,
      sort_direction: currentFilters.value.selects.sortDirection !== 'default' ? currentFilters.value.selects.sortDirection : undefined
    }
    
    // 如果URL中有spot_id参数，添加到请求参数中
    if (route.query.spot_id) {
      params.spot_id = route.query.spot_id
    }

    const response = await getJournalsList(params)
    
    if (response.data && response.data.ret === 0) {
      const responseData = response.data.data
      diaries.value = responseData.retlist
      total.value = responseData.page_size * responseData.total_pages
      currentPage.value = responseData.current_page + 1
    } else {
      ElMessage.error('获取数据失败')
      diaries.value = []
    }
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败，请稍后重试')
    diaries.value = []
  }
}

// 添加重置方法
const handleReset = () => {
  router.replace('/all-diaries')  // 移除URL参数
  fetchDiaries()  // 重新获取数据
}

// 修改处理喜欢/点赞函数
const handleLike = async (diary) => {
  try {
    if (!user) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }
    
    const userId = user.id
    const action = diary.is_liked ? unlikeJournal : likeJournal
    const response = await action(userId, diary.journal_id)
    
    if (response.data.status === 'success') {
      diary.num_likes = response.data.likes_count
      diary.is_liked = !diary.is_liked
      ElMessage.success(diary.is_liked ? '点赞成功' : '已取消点赞')
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchDiaries()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchDiaries()
}

// 处理筛选变化
const handleFilterChange = (filters) => {
  currentFilters.value = filters
  currentPage.value = 1
  fetchDiaries()
}

// 查看详情
const handleViewDetail = (id) => {
  // 在新标签页打开
  window.open(`/diary-detail/${id}`, '_blank')
}

onMounted(() => {
  if (!user) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  // fetchDiaries()
})
</script>

<style scoped lang="scss">
// 添加 mixin 定义
@mixin text-ellipsis($lines) {
  display: -webkit-box;
  -webkit-line-clamp: $lines;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
.filter-search-container {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
  width: 100%;
  max-width: 1200px;
  padding: 0 20px;
}

.filter-section {
  flex: 0 0 75%;  // 修改这里，固定占75%宽度
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.search-button-section {
  flex: 0 0 20%;
  display: flex;
  flex-direction: column;  // 改为纵向排列
  gap: 12px;  // 按钮之间的间距
  padding-bottom: 12px;
}

// 统一按钮样式
.unified-search-button,
.reset-button {
  height: 44px;
  padding: 0 30px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
  border: none;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
  transition: all 0.3s ease;
  width: 100%;  // 让按钮填满容器宽度

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(24, 144, 255, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
}
.reset-button {
  background: linear-gradient(135deg, #67C23A, #85ce61);
}
.filter-panel-container {
  width: 100%;
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

.pagination-container {
  margin-top: 30px;
  padding: 20px 0;
  display: flex;
  justify-content: center;
}

</style>
