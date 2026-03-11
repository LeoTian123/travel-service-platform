import axios from 'axios'

// 获取图数据
export const getGraphData = (id) => {
  return axios.get('/api/routing/list_graph/', {
    params: { id }
  })
}

// 雷达搜索周边景点
export const radarSearch = (params) => {
  return axios({
    url: '/api/routing/radar_search/',
    method: 'get',
    params
  })
}

// 起止点路线规划
export const getBestPathDijkstra = (params) => {
  return axios({
    url: '/api/routing/best_path_dijkstra/',
    method: 'get',
    params
  })
}

// 途径点路线规划
export const getBestPathWithWaypoints = (params) => {
  return axios({
    url: '/api/routing/best_path_circuit/',
    method: 'get',
    params
  })
}