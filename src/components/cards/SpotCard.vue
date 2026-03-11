<template>
  <div class="spot-card">
    <el-image
      :src="spot.image || defaultImage"
      class="card-cover"
      fit="cover"
      @error="handleImageError"
    />
    <div class="card-body">
      <h3 class="card-title">{{ spot.name }}</h3>
      <p class="en-name">{{ spot.enName }}</p>
      <p class="description">{{ spot.description }}</p>
      <div class="stats">
        <span class="stat-item">
          <el-icon><ChatDotRound /></el-icon>
          {{ spot.comments }}
        </span>
        <span class="stat-item">
          <el-icon><Notebook /></el-icon>
          {{ spot.journals }}
        </span>
        <span class="stat-item">
          <el-icon><StarFilled /></el-icon>
          {{ spot.likes }}
        </span>
        <span class="type-tag">{{ spot.type }}</span>
      </div>
      <div class="action-buttons">
        <el-button
          type="primary"
          size="small"
          @click.stop="$emit('view-map', spot.id)"
        >
          <el-icon><Location /></el-icon>
          查看地图
        </el-button>
        <el-button
          type="success"
          size="small"
          @click.stop="$emit('view-diaries', spot.id)"
        >
          <el-icon><Notebook /></el-icon>
          相关日记
        </el-button>
        <el-button
          :type="spot.isLiked ? 'danger' : 'warning'"
          size="small"
          @click.stop="$emit('like', spot)"
        >
          <el-icon><StarFilled /></el-icon>
          {{ spot.isLiked ? '取消点赞' : '点赞' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { 
  ChatDotRound, 
  Notebook, 
  StarFilled, 
  Location 
} from '@element-plus/icons-vue'

defineProps({
  spot: Object
})

const defaultImage = ref('/images/default-spot.jpg')

const handleImageError = (e) => {
  e.target.src = defaultImage.value
}
</script>

<style scoped lang="scss">
.spot-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease;
  cursor: default;

  &:hover {
    transform: translateY(-4px);
  }

  .card-cover {
    width: 100%;
    height: 200px;
    object-fit: cover;
  }

  .card-body {
    padding: 16px;

    .card-title {
      font-size: 18px;
      font-weight: 600;
      margin: 0 0 8px;
      color: #303133;
      display: -webkit-box;
      -webkit-line-clamp: 1;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .en-name {
      color: #909399;
      font-size: 14px;
      margin-bottom: 8px;
      display: -webkit-box;
      -webkit-line-clamp: 1;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .description {
      color: #606266;
      font-size: 14px;
      margin-bottom: 16px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
      line-height: 1.5;
    }

    .stats {
      display: flex;
      align-items: center;
      margin-bottom: 16px;

      .stat-item {
        display: flex;
        align-items: center;
        margin-right: 16px;
        color: #909399;
        font-size: 14px;

        .el-icon {
          margin-right: 4px;
        }
      }

      .type-tag {
        margin-left: auto;
        background-color: #ecf5ff;
        color: #409eff;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
      }
    }

    .action-buttons {
      display: flex;
      justify-content: space-between;

      .el-button {
        flex: 1;
        margin: 0 4px;

        &:first-child {
          margin-left: 0;
        }

        &:last-child {
          margin-right: 0;
        }
      }
    }
  }
}
</style>