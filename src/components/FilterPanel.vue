<template>
  <div class="filter-panel">
    <div class="filter-header">
      <h3 class="filter-title">
        <el-icon><Filter /></el-icon>
        筛选
      </h3>
      <el-button 
        v-if="hasActiveFilters" 
        type="text" 
        @click="resetFilters"
        class="reset-btn"
      >
        重置筛选
      </el-button>
    </div>
    
    <div class="filter-body">
      <!-- 搜索框筛选 -->
      <div v-if="config.search" class="filter-item search-filter">
        <el-input
          v-model="filters.search"
          :placeholder="config.search.placeholder || '搜索...'"
          clearable
          @input="handleFilterChange"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <!-- 下拉选择筛选 -->
      <div 
        v-for="(select, key) in config.selects" 
        :key="key"
        class="filter-item select-filter"
      >
        <label class="filter-label">{{ select.label }}</label>
        <el-select
          v-model="filters.selects[key]"
          :placeholder="select.placeholder || '请选择'"
          clearable
          @change="handleFilterChange"
          class="filter-select"
        >
          <el-option
            v-for="option in select.options"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </div>
      
      <!-- 日期范围筛选 -->
      <div 
        v-if="config.dateRange" 
        class="filter-item date-filter"
      >
        <label class="filter-label">{{ config.dateRange.label }}</label>
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="handleFilterChange"
          class="filter-date"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, reactive, onMounted } from 'vue'
import { Filter, Search } from '@element-plus/icons-vue'

const props = defineProps({
  // 筛选配置
  config: {
    type: Object,
    required: true,
    // 配置示例:
    // {
    //   search: { placeholder: '搜索关键词' },
    //   selects: {
    //     type: {
    //       label: '类型',
    //       placeholder: '选择类型',
    //       options: [
    //         { label: '学校', value: 'school' },
    //         { label: '景区', value: 'scenic' }
    //       ]
    //     }
    //   },
    //   dateRange: { label: '日期范围' }
    // }
  }
})

const emit = defineEmits(['filter-change'])

// 初始化筛选状态
const filters = reactive({
  search: '',
  selects: {},
  dateRange: null
})

// 初始化选择筛选项
onMounted(() => {
  if (props.config.selects) {
    Object.keys(props.config.selects).forEach(key => {
      // 设置默认值为第一个选项
      if (props.config.selects[key].options && props.config.selects[key].options.length > 0) {
        filters.selects[key] = props.config.selects[key].options[0].value
      }
    })
    // 初始化完成后触发一次筛选
    handleFilterChange()
  }
})

// 重置所有筛选
const resetFilters = () => {
  filters.search = ''
  if (props.config.selects) {
    Object.keys(props.config.selects).forEach(key => {
      // 重置为第一个选项
      if (props.config.selects[key].options && props.config.selects[key].options.length > 0) {
        filters.selects[key] = props.config.selects[key].options[0].value
      }
    })
  }
  filters.dateRange = null
  handleFilterChange()
}

// 判断是否有激活的筛选条件
const hasActiveFilters = computed(() => {
  return (
    (filters.search && filters.search.trim() !== '') ||
    Object.values(filters.selects).some(val => val !== '') ||
    (filters.dateRange && filters.dateRange.length === 2)
  )
})

// 处理筛选变化
const handleFilterChange = () => {
  emit('filter-change', { ...filters })
}

// 监听配置变化，更新筛选状态
watch(
  () => props.config,
  (newConfig) => {
    // 更新选择筛选项
    if (newConfig.selects) {
      Object.keys(newConfig.selects).forEach(key => {
        if (!(key in filters.selects)) {
          filters.selects[key] = ''
        }
      })
    }
  },
  { deep: true }
)
</script>

<style scoped lang="scss">
.filter-panel {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  .filter-title {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0;
    font-size: 16px;
    color: #303133;
  }
  
  .reset-btn {
    color: #409EFF;
    padding: 0;
  }
}

.filter-body {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.filter-item {
  margin-bottom: 12px;
  
  &.search-filter {
    width: 100%;
  }
  
  &.select-filter {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 200px;
  }
  
  &.date-filter {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
}

.filter-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.filter-select,
.filter-date {
  width: 100%;
}

@media (max-width: 768px) {
  .filter-body {
    flex-direction: column;
  }
  
  .filter-item {
    width: 100%;
  }
}
</style>
