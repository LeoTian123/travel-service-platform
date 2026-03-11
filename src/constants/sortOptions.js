// 排序方式常量
export const SORT_TYPES = {
    DEFAULT: 'default',
    COMMENTS: 'comments',
    LIKES: 'likes'
  }
  
  // 排序方式选项（用于筛选组件）
  export const SORT_TYPE_OPTIONS = [
    { label: '默认排序', value: SORT_TYPES.DEFAULT },
    { label: '热度排序', value: SORT_TYPES.COMMENTS },
    { label: '评价排序', value: SORT_TYPES.LIKES }
  ]
  
  // 排序方向常量
  export const SORT_DIRECTIONS = {
    DEFAULT: 'default',
    REV: 'rev',
  }
  
  // 排序方向选项（用于筛选组件）
  export const SORT_DIRECTION_OPTIONS = [
    { label: '默认方向/从高到低', value: SORT_DIRECTIONS.DEFAULT },
    { label: '倒序方向/从低到高', value: SORT_DIRECTIONS.REV },
  ]