<template>
  <div class="tourism-container">
    <Sidebar />
    <div class="main-content">
      <h1 class="page-title">旅游推荐</h1>

      <!-- 筛选面板与搜索按钮 -->
      <div class="filter-search-container">
        <div class="filter-section">
          <FilterPanel
            :config="filterConfig"
            @filter-change="handleFilterChange"
            class="filter-panel-container"
          />
        </div>

        <!-- 统一搜索按钮 -->
        <div class="search-button-section">
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

      <!-- 景点卡片列表 -->
      <!-- 替换原有的卡片循环部分 -->
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
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Sidebar from '@/components/Sidebar.vue'
import FilterPanel from '@/components/FilterPanel.vue'
import SpotCard from '@/components/cards/SpotCard.vue'
import { getAttractionsList, likeAttraction, unlikeAttraction } from '@/api/attractions'
import { SPOT_TYPE_OPTIONS, SPOT_TYPES } from '@/constants/spotTypes'
import { SORT_TYPE_OPTIONS, SORT_TYPES, SORT_DIRECTION_OPTIONS, SORT_DIRECTIONS  } from '@/constants/sortOptions'
import {
  Search,
  Location,
  Clock,
  Close,
  StarFilled,
  ChatDotRound,
  Notebook
} from '@element-plus/icons-vue'

const router = useRouter()
const defaultImage = ref('/images/default-spot.jpg')
const spots = ref([])
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
// 获取用户信息
const user = JSON.parse(localStorage.getItem('user'))

// 筛选配置
const filterConfig = reactive({
  search: { placeholder: '搜索景点名称' },
  selects: {
    type: {
      label: '类型',
      placeholder: '选择景点类型',
      options: SPOT_TYPE_OPTIONS
    },
    sortType: {
      label: '排序方式',
      placeholder: '选择排序方式',
      options: SORT_TYPE_OPTIONS
    },
    sortDirection: {
      label: '排序方向',
      placeholder: '选择排序方向',
      options: SORT_DIRECTION_OPTIONS
    }
  }
})

// 当前筛选条件
const currentFilters = ref({
  search: '',
  selects: {
    type: SPOT_TYPES.ALL,          // 默认选择"全部"
    sortType: SORT_TYPES.DEFAULT,  // 默认选择"默认排序"
    sortDirection: SORT_DIRECTIONS.DEFAULT  // 默认选择"默认方向"
  }
})

// 获取景点列表
const fetchSpots = async () => {
  try {
    const params = {
      page_num: currentPage.value - 1,
      page_size: pageSize.value,
      user_id: user.id,  // 添加用户ID
      keyword: currentFilters.value.search || undefined,
      type: currentFilters.value.selects.type !== SPOT_TYPES.ALL ? currentFilters.value.selects.type : undefined,
      sort_type: currentFilters.value.selects.sortType !== SORT_TYPES.DEFAULT ? currentFilters.value.selects.sortType : undefined,
      sort_direction: currentFilters.value.selects.sortDirection !== SORT_DIRECTIONS.DEFAULT ? currentFilters.value.selects.sortDirection : undefined
    }

    const response = await getAttractionsList(params)
    
    if (response.data && response.data.ret === 0) {
      const responseData = response.data.data
      spots.value = responseData.retlist.map(item => ({
        id: item.id,
        name: item.cnName,           // 修改：使用 cnName 作为名称
        enName: item.enName || '',   // 保持不变
        description: item.description || '暂无描述',
        image: item.img_url,         // 修改：使用 img_url 作为图片地址
        comments: item.num_comment_quna || 0,  // 修改：使用 num_comment_quna
        journals: item.num_journals || 0,  // 新增journals字段
        likes: item.num_likes || 0,  // 保持不变
        type: item.type || '未分类',  // 保持不变
        isLiked: item.is_liked || false  // 保持不变
      }))

      total.value = responseData.page_size * responseData.total_pages
      currentPage.value = responseData.current_page + 1
    } else {
      ElMessage.error(response.data.msg || '没有符合条件的数据')
      spots.value = []
    }
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败，请稍后重试')
    spots.value = []
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchSpots()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchSpots()
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

// 修改查看相关日记的方法
const handleViewDiaries = (id) => {
  router.push({
    path: '/all-diaries',
    query: { spot_id: id }
  })
}

// 处理筛选变化
const handleFilterChange = (filters) => {
  currentFilters.value = filters
  currentPage.value = 1
  fetchSpots()
}

// 处理搜索按钮点击
const handleSearchButtonClick = () => {
  fetchSpots()
}

// 修改点赞处理方法
const handleLike = async (spot) => {  // 改为接收整个spot对象
  try {
    if (!user) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }
    
    const userId = user.id
    const action = spot.isLiked ? unlikeAttraction : likeAttraction
    const response = await action(userId, spot.id)  // 使用spot.id
    
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

// 将用户检查移到最开始
onMounted(() => {
  if (!user) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  // fetchSpots()
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
  flex: 0 0 75%;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.filter-panel-container {
  width: 100%;
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-button-section {
  flex: 0 0 20%;
  display: flex;
  justify-content: flex-end;
  align-items: flex-end;
  padding-bottom: 12px;
}

.unified-search-button {
  height: 44px;
  padding: 0 30px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
  background: linear-gradient(135deg, #409EFF, #1890ff);
  border: none;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(24, 144, 255, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
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