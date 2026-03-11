<template>
  <div class="diary-card" @click="$emit('click')">
    <el-image
      :src="diary.img_cover ? getImageUrl(diary.img_cover) : defaultCover"
      class="card-cover"
      fit="cover"
    >
      <template #error>
        <div class="image-slot">
          <div class="no-cover">无封面</div>
        </div>
      </template>
    </el-image>
    <div class="card-body">
      <div class="card-header">
        <span class="spot-tag">
          <el-icon><Location /></el-icon>
          {{ diary.spot_name }}
        </span>
        <span class="date">{{ diary.date }}</span>
      </div>
      <h3 class="title">{{ diary.title }}</h3>
      <p class="content">{{ diary.content }}</p>
      <div class="author" v-if="showAuthor">
        <span>发布者：{{ diary.user_name }}</span>
      </div>
      <div class="card-actions">
        <el-button
          :type="diary.is_liked ? 'danger' : 'warning'"
          size="small"
          @click.stop="$emit('like', diary)"
        >
          <el-icon><StarFilled /></el-icon>
          {{ diary.num_likes }} {{ diary.is_liked ? '已喜欢' : '喜欢' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Location, StarFilled } from '@element-plus/icons-vue'
import { getImageUrl } from '@/api/journals'

defineProps({
  diary: Object,
  showAuthor: {
    type: Boolean,
    default: true
  }
})

const defaultCover = '/images/default-diary.jpg'
</script>

<style scoped lang="scss">
.diary-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease;
  cursor: pointer;

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

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      .spot-tag {
        background: #f0f2f5;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        color: #666;
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .date {
        font-size: 12px;
        color: #999;
      }
    }

    .title {
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

    .content {
      color: #606266;
      font-size: 14px;
      margin-bottom: 12px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
      line-height: 1.5;
    }

    .author {
      font-size: 14px;
      color: #909399;
      margin-bottom: 12px;
    }

    .card-actions {
      display: flex;
      justify-content: flex-end;

      .el-button {
        padding: 8px 16px;
        
        .el-icon {
          margin-right: 4px;
        }
      }
    }
  }
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
}

.no-cover {
  font-size: 16px;
  color: #909399;
  font-weight: bold;
}
</style>