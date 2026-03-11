import axios from 'axios'

// 获取日记列表
export const getJournalsList = (params) => {
  return axios({
    method: 'get',
    url: '/api/journals/list/',
    params: params
  })
}

// 点赞日记
export const likeJournal = (userId, journalId) => {
  return axios({
    method: 'post',
    url: '/api/journals/like/',
    data: {
      user_id: userId,
      journal_id: journalId
    }
  })
}

// 取消点赞日记
export const unlikeJournal = (userId, journalId) => {
  return axios({
    method: 'post',
    url: '/api/journals/unlike/',
    data: {
      user_id: userId,
      journal_id: journalId
    }
  })
}

// 获取图片
export const getImageUrl = (filename) => {
    if (!filename) return null
    return `/api/journals/get_journal_image/${filename}`
  }

// 获取日记详情
export const getJournalDetail = (journalId, userId) => {
  return axios({
    method: 'get',
    url: '/api/journals/list_detail/',
    params: {
      journal_id: journalId,
      user_id: userId
    }
  })
}

// 获取用户喜欢的日记列表
export const getUserLikedJournals = (params) => {
  return axios({
    method: 'get',
    url: '/api/journals/list_user/',
    params: params
  })
}

// 获取景点列表
export const getAttractionsList = () => {
  return axios({
    method: 'get',
    url: '/api/journals/list_attraction_id_and_name/'
  })
}

// 创建新日记
export const createJournal = (formData) => {
  return axios({
    method: 'post',
    url: '/api/journals/create/',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}