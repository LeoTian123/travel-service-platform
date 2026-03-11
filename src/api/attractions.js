import axios from 'axios'

export const getAttractionsList = (params) => {
  return axios({
    method: 'get',
    url: '/api/attractions/list/',  // 添加末尾斜杠以匹配后端路径
    params: params
  })
}

// 添加点赞方法
export const likeAttraction = (userId, postId) => {
  return axios({
    method: 'post',
    url: '/api/attractions/like/',
    data: {
      user_id: userId,
      post_id: postId
    }
  })
}

// 添加取消点赞方法
export const unlikeAttraction = (userId, postId) => {
  return axios({
    method: 'post',
    url: '/api/attractions/unlike/',
    data: {
      user_id: userId,
      post_id: postId
    }
  })
}

// 添加获取用户点赞景点列表方法
export const getUserLikedAttractions = (params) => {
  return axios({
    method: 'get',
    url: '/api/attractions/list_user/',
    params: params
  })
}

// 添加基于用户协同过滤的推荐方法
export const getUBCFRecommendations = (userId, count = 10) => {
  return axios({
    method: 'get',
    url: '/api/attractions/list_UBCF/',
    params: {
      user_id: userId,
      count: count
    }
  })
}