<template>
  <div class="page-container">
    <!-- 地图容器 -->
    <div class="map-wrapper">

      <!-- 添加返回按钮 -->
      <div class="back-button" @click="goBack">
        <span class="back-icon">←</span>
        <span>返回</span>
      </div>

      <div id="map-container" style="width: 100%; height: 99vh"></div>
      <div v-if="currentSpot" class="spot-selector" :class="{ expanded: isExpanded }">
        <!-- 左侧景点栏保持不变 -->
      </div>
      <!-- 图例 -->
      <div class="map-legend">
        <div v-for="(type, key) in SPOT_TYPES" :key="key" class="legend-item">
          <span class="legend-marker" :style="{ background: type.color }">{{ type.icon }}</span>
          <span>{{ type.name }}</span>
        </div>
      </div>
      <!-- 浮动式详情面板 -->
      <div v-if="selectedSpot" class="spot-details" :style="detailPosition">
        <div class="details-content">
          <h2>{{ selectedSpot.name }}</h2>
          <img v-if="selectedSpot.details?.image" :src="selectedSpot.details.image" alt="景点图片" />
          <p v-if="selectedSpot.details?.description">{{ selectedSpot.details.description }}</p>
          <p v-else>暂无详情描述</p>
          <button class="close-btn" @click="selectedSpot = null">×</button>
        </div>
      </div>
    </div>

    <!-- 路线选择组件 -->
    <div class="route-planner">
      <div class="planner-header">
            <button 
              :class="{ active: routeMode === 'start-end' }" 
              @click="routeMode = 'start-end'">
              起止路线规划
            </button>
            <button 
              :class="{ active: routeMode === 'waypoints' }" 
              @click="routeMode = 'waypoints'">
              途径点路线规划
            </button>
          </div>
          <div class="planner-body">
            <!-- 起止路线规划 -->
            <div v-if="routeMode === 'start-end'">
              <div class="input-group start-point">
                <label>起</label>
                <select v-model="startPoint">
                  <option v-for="spot in allSpots.slice(1)" :key="spot.id" :value="spot.id">
                    {{ spot.name }}
                  </option>
                </select>
              </div>
              <div class="input-group end-point">
                <label>终</label>
                <select v-model="endPoint">
                  <option v-for="spot in allSpots.slice(1)" :key="spot.id" :value="spot.id">
                    {{ spot.name }}
                  </option>
                </select>
              </div>
              <div class="input-group">
                <label>优先</label>
                <select v-model="priority">
                  <option value="distance">最短路径</option>
                  <option value="time">最短时间</option>
                  <option value="walk_time">只走路最短时间</option>
                </select>
              </div>
              <button class="plan-route-btn" @click="planRoute">开始规划</button>
        </div>

        <!-- 途径点路线规划 -->
        <div v-if="routeMode === 'waypoints'">
          <div class="input-group start-point">
            <label>起</label>
            <select v-model="startPoint">
              <option v-for="spot in allSpots.slice(1)" :key="spot.id" :value="spot.id">
                {{ spot.name }}
              </option>
            </select>
          </div>
          <div class="input-group waypoints">
            <label>经</label>
            <div class="waypoints">
              <div v-for="(point, index) in waypoints" :key="index" class="waypoint">
                <select v-model="waypoints[index]">
                  <option v-for="spot in allSpots.slice(1)" :key="spot.id" :value="spot.id">
                    {{ spot.name }}
                  </option>
                </select>
                <button @click="removeWaypoint(index)">-</button>
              </div>
              <button @click="addWaypoint">+</button>
            </div>
          </div>
          <div class="input-group">
            <label>优先</label>
            <select v-model="priority">
              <option value="distance">最短路径</option>
              <option value="time">最短时间</option>
              <option value="walk_time">只走路最短时间</option>
            </select>
          </div>
          <button class="plan-route-btn" @click="planRoute">开始规划</button>
        </div>
      </div>

      <!-- 景点查询 -->
      <div class="planner-header">
        景点查询
      </div>
      <div class="planner-body">
        <!-- 查询景点 -->
        <div class="input-group center-point">
          <label>中心点</label>
          <select v-model="selectedSpotForQuery">
            <option v-for="spot in allSpots.slice(1)" :key="spot.id" :value="spot.id">
              {{ spot.name }}
            </option>
          </select>
        </div>
        <!-- 查询类型 -->
        <div class="input-group">
          <label>周围</label>
          <select v-model="queryType">
            <option value="">全部种类</option>
            <option v-for="(type, key) in SPOT_TYPES" :key="key" :value="key">
              {{ type.name }}
            </option>
          </select>
        </div>
        <!-- 查询数量 -->
        <div class="input-group">
          <label>数量</label>
          <select v-model="queryLimit">
            <option v-for="n in [5,10,15,20,25,30,35,40,45,50]" :key="n" :value="n">
              {{ n }}
            </option>
          </select>
        </div>
        <!-- 优先 -->
        <div class="input-group">
          <label>优先</label>
            <select v-model="priority">
              <option value="distance">最短路径</option>
              <option value="time">最短时间</option>
              <option value="walk_time">只走路最短时间</option>
            </select>
        </div>
        <button class="query-btn" @click="queryNearby">查询</button>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { loadAMap } from '@/utils/amapLoader'
import { 
  getGraphData, 
  getBestPathDijkstra, 
  getBestPathWithWaypoints, 
  radarSearch 
} from '@/api/graph'

//响应式变量
const isExpanded = ref(false)
const map = ref(null) // 将地图实例存储为响应式变量
const currentSpot = ref(null)
const route = useRoute()
const selectedSpot = ref(null)
const detailPosition = ref({
  top: 'auto',
  bottom: 'auto',
  left: 'auto',
  right: 'auto'
})
const highlightedMarker = ref(null) //存储当前高亮标记

//路线规划相关变量
const routeMode = ref('start-end') // 路线规划模式：'start-end' 或 'waypoints'
const allSpots = ref([]) // 存储所有景点
const startPoint = ref('') // 起点
const endPoint = ref('') // 终点
const waypoints = ref([]) // 途经点
const priority = ref('distance') // 优先级

// 景点查询相关变量
const selectedSpotForQuery = ref('') // 用户选择的中心点
const queryType = ref('') // 查询类型（厕所或超市）
const queryLimit = ref(0) // 查询数量，默认前 0 个

//函数
const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

const focusOnSpot = (subSpot) => {
  if (!map.value) {
    console.error('地图实例未初始化')
    return
  }
  
  // 清除之前的高亮
  if (highlightedMarker.value) {
    resetMarkerStyle(highlightedMarker.value)
    highlightedMarker.value = null
  }
  
  const [lng, lat] = virtualToReal(subSpot.x, subSpot.y)
  console.log('移动至坐标:', lng, lat)
  
  // 使用更精确的匹配方式
  const targetPos = new AMap.LngLat(lng, lat)
  const tolerance = 0.00001 // 更小的容差范围
  
  map.value.panTo([lng, lat])
  map.value.setZoom(30, false)
  
  // 高亮当前标记
  const markers = map.value.getAllOverlays('marker')
  markers.forEach(m => {
    const pos = m.getPosition()
    // 使用高德地图的equals方法进行精确比较
    if (targetPos.equals(pos, tolerance)) {
      // 使用新的高亮效果
      m.setContent(createHighlightMarkerContent(subSpot))
      highlightedMarker.value = m
    }
  })
  
  setDetailPosition(lng, lat)
}

// 专门的高亮标记内容
const createHighlightMarkerContent = (spot) => {
  const markerSize = 18 // 比普通标记稍大
  const highlightColor = '#FFD700' // 金色
  const highlightBorder = '#FFA500' // 橙色边框
  
  return `
    <div style="display:flex; flex-direction:column; align-items:center;">
      <div style="
        width:${markerSize}px; 
        height:${markerSize}px; 
        background:${highlightColor};
        border-radius:50%;
        display:flex;
        justify-content:center;
        align-items:center;
        color:#FFFFFF;
        font-size:14px;
        font-weight:bold;
        border:3px solid ${highlightBorder};
        box-shadow:0 2px 8px rgba(0,0,0,0.4);
        animation: pulse 1s infinite alternate;
      "></div>
      <div style="
        margin-top:10px;
        padding:3px 10px;
        background:white;
        color:#333;
        font-size:14px;
        font-weight:bold;
        border-radius:4px;
        box-shadow:0 2px 4px rgba(0,0,0,0.3);
        border:1px solid ${highlightBorder};
      ">${spot.name}</div>
    </div>
  `
}

//创建标记内容的函数
const createMarkerContent = (spot, isHighlighted = false) => {
  const typeInfo = SPOT_TYPES.value[spot.type] || SPOT_TYPES.value['路口'] // 使用默认类型
  const markerSize = isHighlighted ? 20 : 16
  const markerColor = isHighlighted ? '#FFD700' : typeInfo.color
  
  return `
    <div style="display:flex; flex-direction:column; align-items:center;">
      <div style="
        width:${markerSize}px; 
        height:${markerSize}px; 
        background:${markerColor};
        border-radius:50%;
        display:flex;
        justify-content:center;
        align-items:center;
        color:white;
        font-size:12px;
        border:2px solid white;
        box-shadow:0 2px 4px rgba(0,0,0,0.3);
      ">${typeInfo.icon}</div>
      <div style="margin-top:4px; padding:2px 6px; background:white; border-radius:4px;">
        ${spot.name}
      </div>
    </div>
  `
}


// 新增：重置标记样式
const resetMarkerStyle = (marker) => {
  const pos = marker.getPosition()
  const realPos = [pos.lng, pos.lat]
  const spot = findSpotByPosition(realPos)
  if (spot) {
    marker.setContent(createMarkerContent(spot))
  }
}

// 新增：根据位置查找景点
const findSpotByPosition = ([lng, lat]) => {
  if (!currentSpot.value) return null
  
  // 检查主景点
  const mainSpotPos = virtualToReal(currentSpot.value.center.x, currentSpot.value.center.y)
  if (Math.abs(mainSpotPos[0] - lng) < 0.0001 && Math.abs(mainSpotPos[1] - lat) < 0.0001) {
    return { ...currentSpot.value.center, name: currentSpot.value.name }
  }
  
  // 检查子景点
  return currentSpot.value.subSpots.find(sub => {
    const subPos = virtualToReal(sub.x, sub.y)
    return Math.abs(subPos[0] - lng) < 0.0001 && Math.abs(subPos[1] - lat) < 0.0001
  })
}

// 根据点击位置设置详情面板位置
const setDetailPosition = (lng, lat) => {
  // 获取地图容器尺寸
  const container = document.getElementById('map-container')
  const rect = container.getBoundingClientRect()
  
  // 将经纬度转换为屏幕坐标
  const pixel = map.value.lngLatToContainer([lng, lat])
  
  // 计算最佳显示位置
  const position = { top: 'auto', bottom: 'auto', left: 'auto', right: 'auto' }
  
  if (pixel.y < rect.height / 2) {
    position.top = `${pixel.y + 20}px`  // 如果在上面半区，详情显示在下方
  } else {
    position.bottom = `${rect.height - pixel.y + 20}px`  // 如果在下面半区，详情显示在上方
  }
  
  if (pixel.x < rect.width / 2) {
    position.left = `${pixel.x + 20}px`  // 如果在左半区，详情显示在右侧
  } else {
    position.right = `${rect.width - pixel.x + 20}px`  // 如果在右半区，详情显示在左侧
  }
  
  detailPosition.value = position
}


function showDetails(spot) {
  selectedSpot.value = spot
}

// 坐标转换函数
// 将常量改为响应式变量
const SPOT_TYPES = ref({})
const PATH_TYPES = ref({})
const VIRTUAL_RANGE = ref({
  minX: 0,
  maxX: 1000,
  minY: 0,
  maxY: 1000
})
const REAL_BOUNDS = ref({
  minLng: 116.397,
  maxLng: 116.405,
  minLat: 39.915,
  maxLat: 39.920
})

// 修改坐标转换函数以使用响应式数据
function virtualToReal(x, y) {
  const lng = REAL_BOUNDS.value.minLng + 
    (x - VIRTUAL_RANGE.value.minX) * (REAL_BOUNDS.value.maxLng - REAL_BOUNDS.value.minLng) / 
    (VIRTUAL_RANGE.value.maxX - VIRTUAL_RANGE.value.minX);
  
  const lat = REAL_BOUNDS.value.maxLat - 
    (y - VIRTUAL_RANGE.value.minY) * (REAL_BOUNDS.value.maxLat - REAL_BOUNDS.value.minLat) / 
    (VIRTUAL_RANGE.value.maxY - VIRTUAL_RANGE.value.minY);
  
  return [lng, lat];
}


// 路由参数

const spotId = route.params.id || route.query.id // 兼容两种传参方式




onMounted(async () => {
  try {
    // 获取图数据
    const { data: response } = await getGraphData(spotId)
    if (response.ret !== 0) {
      console.error('获取图数据失败')
      return
    }

    const graphData = response.data
    // 更新全局常量
    SPOT_TYPES.value = graphData.types.spotTypes
    PATH_TYPES.value = graphData.types.pathTypes
    VIRTUAL_RANGE.value = graphData.bounds.virtual
    REAL_BOUNDS.value = graphData.bounds.real

    // 构造spotData结构
    const spotData = {
      name: graphData.name,
      center: graphData.center,
      subSpots: graphData.nodes,
      edges: graphData.edges
    }

    // // 反向边
    // const originalLength = spotData.edges.length;
    // for (let i = 0; i < originalLength; i++) {
    //   const edge = spotData.edges[i];
    //   spotData.edges.push({
    //     from: edge.to,
    //     to: edge.from,
    //     vehicle: edge.vehicle,
    //   });
    // }

    // 将主景点和子景点合并到 allSpots 中
    allSpots.value = [
      { id: 'main', name: spotData.name, ...spotData.center },
      ...spotData.subSpots.map(spot => ({
        id: spot.id,
        name: spot.name,
        x: spot.x,
        y: spot.y
      }))
    ]
    
    currentSpot.value = spotData

    // 加载高德地图 SDK
    const AMap = await loadAMap()

    // 初始化地图
    map.value = new AMap.Map('map-container', {
      zoom: 17,
      center: virtualToReal(spotData.center.x, spotData.center.y),
      viewMode: '2D',
      showIndoorMap: false,
      zoomEnable: true,
      dragEnable: true,
      rotateEnable: false,
      pitchEnable: false,
      layers: [],  // 不加载任何图层
      mapStyle: 'amap://styles/normal',  // 使用普通样式
      features: []  // 不显示任何要素
    })

    // 添加主景点标记
    const mainMarker = new AMap.Marker({
      position: virtualToReal(spotData.center.x, spotData.center.y),
      content: createMarkerContent({ 
        ...spotData.center,
        type: '地标', // 改为后端定义的类型
        name: spotData.name 
      }),
      offset: new AMap.Pixel(-15, -15)
    })
    map.value.add(mainMarker)

    // 添加子景点标记
    spotData.subSpots.forEach((subSpot) => {
      const subMarker = new AMap.Marker({
        position: virtualToReal(subSpot.x, subSpot.y),
        content: createMarkerContent(subSpot),
        offset: new AMap.Pixel(-14, -10)
      })
      
      // 显示景点信息
      subMarker.on('click', () => {
        selectedSpot.value = subSpot
        focusOnSpot(subSpot)
        // 清除其他矩形的的高亮状态
        map.value.getAllOverlays('polygon').forEach((polygon) => {
          polygon.setOptions({
            strokeColor: '#f5f5f5', // 恢复默认边框颜色
            fillColor: '#87ceeb', // 恢复默认填充颜色
            fillOpacity: 0.3, // 恢复默认填充透明度
          });
        });
        // 设置当前矩形为高亮状态
        rectangle.setOptions({
          strokeColor: '#7ab8cc', // 高亮边框颜色
          fillOpacity: 0.5, // 增加填充透明度
        });
      })

      map.value.add(subMarker)

    })

    // 增强版边线绘制
    // 增强版边线绘制
    spotData.edges.forEach((edge) => {
      const fromSpot = spotData.subSpots.find(s => s.id === edge.from)
      const toSpot = spotData.subSpots.find(s => s.id === edge.to)

      if (fromSpot && toSpot) {
        const pathType = PATH_TYPES.value[edge.vehicle] || PATH_TYPES.value.walk // 使用vehicle属性
        const line = new AMap.Polyline({
          path: [
            virtualToReal(fromSpot.x, fromSpot.y),
            virtualToReal(toSpot.x, toSpot.y)
          ],
          strokeColor: pathType.color,
          strokeWeight: pathType.weight,
          strokeStyle: 'solid',
          strokeOpacity: 0.8,
          lineJoin: 'round',
          extData: { from: edge.from, to: edge.to, vehicle: edge.vehicle }
        })

        map.value.add(line)
      }
    })
  

    // 调整视图以显示所有点
    map.value.setFitView()
  } catch (error) {
    console.error('加载高德地图失败:', error)
  }
})

//路线规划函数
// 添加途经点
const addWaypoint = () => {
  waypoints.value.push('')
}

// 移除途经点
const removeWaypoint = (index) => {
  waypoints.value.splice(index, 1)
}

// 判断值是否有效（不为 undefined、null 或空字符串）
const isValidValue = (value) => {
  return value !== undefined && value !== null && value !== ''
}

// 规划路线
const planRoute = async () => {
  if (!isValidValue(startPoint.value)) {
    alert('请填写起点')
    return
  }

  if (routeMode.value === 'start-end') {
    if (!isValidValue(endPoint.value)) {
      alert('请填写终点')
      return
    }

    try {
      // 调用接口获取路径
      const response = await getBestPathDijkstra({
        id: spotId, // 当前景点 ID
        start: startPoint.value, // 起点 ID
        end: endPoint.value, // 终点 ID
        weight: priority.value // 优先级（如 time、distance 等）
      })

      if (response.data && response.data.ret === 0) {
        const { path, dist } = response.data.data // 从 data 中解构获取 path 和 dist
        console.log('规划路径成功:', path)

        // 重置所有路径样式
        resetPathStyles()
        // 清除之前的高亮标记
        clearHighlightedMarkers()

        // 高亮规划的路径 弹窗
        highlightPlannedPath(path)
        const pathNames = path.map(id => allSpots.value.find(spot => spot.id === id)?.name || id)
        alert(`规划路径成功，总距离/时间: ${dist}\n路径: ${pathNames.join(' -> ')}`)
      } else {
        console.error('规划路径失败:', response.data.msg || '未知错误')
        alert('规划路径失败，请检查输入')
      }
    } catch (error) {
      console.error('规划路径请求失败:', error)
      alert('规划路径请求失败，请稍后重试')
    }
  }else if (routeMode.value === 'waypoints') {
    try {
      // 调用接口 2 获取路径
      const response = await getBestPathWithWaypoints({
        id: spotId, // 当前景点 ID
        start: startPoint.value, // 起点 ID
        nodes: JSON.stringify(waypoints.value), // 途径点 ID 列表，逗号分隔
        weight: priority.value // 优先级（如 time、distance 等）
      })

      if (response.data && response.data.ret === 0) {
        const { dist, path, path_extracted } = response.data.data // 从 data 中解构获取
        console.log('规划路径成功:', path)

        // 重置所有路径样式
        resetPathStyles()
        // 清除之前的高亮标记
        clearHighlightedMarkers()

        // 高亮规划的路径 弹窗
        highlightPlannedPath(path)
        const pathNames = path.map(id => allSpots.value.find(spot => spot.id === id)?.name || id)
        alert(`规划路径成功，总距离/时间: ${dist}\n路径: ${pathNames.join(' -> ')}`)
      } else {
        console.error('规划路径失败:', response.data.msg || '未知错误')
        alert('规划路径失败，请检查输入')
      }
    } catch (error) {
      console.error('规划路径请求失败:', error)
      alert('规划路径请求失败，请稍后重试')
    }
  }else {
    alert('当前模式不支持起止路线规划')
  }
}

// 高亮规划的路径
const highlightPlannedPath = (path) => {
  if (!map.value) {
    console.error('地图实例未初始化')
    return
  }

  // 遍历路径中的每一段，找到对应的线条并高亮
  for (let i = 0; i < path.length - 1; i++) {
    const fromId = path[i]
    const toId = path[i + 1]

    // 找到对应的线条
    const lines = map.value.getAllOverlays('polyline')
    lines.forEach(line => {
      const extData = line.getExtData()
      if (extData && (
        (extData.from === fromId && extData.to === toId) ||
        (extData.from === toId && extData.to === fromId)
      )) {
        // 根据路线类型动态设置高亮颜色
        let highlightColor = '#FFD700'
        if (priority.value === 'time') {
          if (extData.vehicle === 'bike' && extData.vehicle === 'both')
            highlightColor = '#0091ff'
          else
            highlightColor = '#34c759'
        }

        // 高亮线条，不设置箭头
        line.setOptions({
          strokeColor: highlightColor,
          strokeWeight: 15,
          strokeOpacity: 1,
          strokeStyle: 'solid',
          lineJoin: 'round'
        })
      }
    })
  }
}

//恢复默认路径样式
//恢复默认路径样式
const resetPathStyles = () => {
  if (!map.value) {
    console.error('地图实例未初始化')
    return
  }

  // 遍历所有的 Polyline（路径）
  const lines = map.value.getAllOverlays('polyline')
  lines.forEach(line => {
    const extData = line.getExtData() // 获取线条的扩展数据
    if (extData && extData.vehicle) {
      const pathType = PATH_TYPES.value[extData.vehicle] || PATH_TYPES.value.walk // 根据 vehicle 获取样式
      line.setOptions({
        strokeColor: pathType.color,
        strokeWeight: pathType.weight,
        strokeOpacity: 0.8,
        strokeStyle: 'solid',
        lineJoin: 'round'
      })
    }
  })
}

// 查询周围地点的函数
const queryNearby = async () => {
  if (!isValidValue(selectedSpotForQuery.value)) {
    alert('请选择一个中心点')
    return
  }

  if (queryLimit.value <= 0) {
    alert('请选择要查询周围几个点')
    return
  }

  try {
    // 调用接口查询周围地点
    const requestParams = {
          id: spotId, // 当前景点 ID
          start: selectedSpotForQuery.value, // 中心点 ID
          weight: priority.value, // 优先级（如 time、distance 等）
          k: queryLimit.value, // 查询数量
        }
        
    // 只有当不是"全部种类"时才添加 node_type 参数
    if (queryType.value !== '') {
      requestParams.node_type = queryType.value
    }
    
    const response = await radarSearch(requestParams)

    if (response.data && response.data.ret === 0) {
      const nearbyData = response.data.data // 保存返回的 data 数组
      console.log('查询成功:', nearbyData)

      // 清除之前的高亮标记
      clearHighlightedMarkers()
      // 重置所有路径样式
      resetPathStyles()

      // 高亮查询到的地点
      highlightNearbySpots(nearbyData)

      // TODO: 在地图上展示查询结果
      const alertStr1 = `查询 ${allSpots.value.find(spot => spot.id === selectedSpotForQuery.value)?.name} 周围的 ${queryType.value === '' ? '全部种类' : queryType.value}`
      const nearbyDataNames = nearbyData.map(id => allSpots.value.find(spot => spot.id === id)?.name || id)
      const alertStr2 = `查询成功: ${nearbyDataNames.join(', ')}`
      alert(alertStr1 + '\n' + alertStr2)
      
    } else {
      console.error('查询失败:', response.data.msg || '未知错误')
      alert('查询失败，请检查输入')
    }
  } catch (error) {
    console.error('查询请求失败:', error)
    alert('查询请求失败，请稍后重试')
  }
}

//恢复地点默认样式
const clearHighlightedMarkers = () => {
  if (!map.value) {
    console.error('地图实例未初始化')
    return
  }

  // 遍历所有的 Marker（标记）
  const markers = map.value.getAllOverlays('marker')
  markers.forEach(marker => {
    const extData = marker.getExtData()
    if (extData && extData.isHighlighted) {
      // 恢复默认样式
      const pos = marker.getPosition()
      const realPos = [pos.lng, pos.lat]
      const spot = findSpotByPosition(realPos)
      if (spot) {
        marker.setContent(createMarkerContent(spot))
      }
      // 移除高亮标记
      marker.setExtData({ isHighlighted: false })
    }
  })
}

// 高亮查询到的地点
const highlightNearbySpots = (nearbyData) => {
  if (!map.value) {
    console.error('地图实例未初始化')
    return
  }

  nearbyData.forEach(id => {
    const spot = allSpots.value.find(s => s.id === id)
    if (spot) {
      const [lng, lat] = virtualToReal(spot.x, spot.y)
      const targetPos = new AMap.LngLat(lng, lat)

      // 遍历所有的 Marker（标记）
      const markers = map.value.getAllOverlays('marker')
      markers.forEach(marker => {
        const pos = marker.getPosition()
        if (targetPos.equals(pos)) {
          // 设置高亮样式
          marker.setContent(createHighlightMarkerContent(spot))
          marker.setExtData({ isHighlighted: true }) // 标记为高亮
        }
      })
    }
  })
}

// 添加路由器实例
const router = useRouter()

// 添加返回函数
const goBack = () => {
  router.back()
}

</script>

<style scoped lang="scss">
.page-container {
  display: flex;
  width: 100%;
  height: 100vh;
}
/* 增强地图容器样式 */
.map-wrapper {
  flex:3;/* 占 75% 宽度 */
  position: relative;
  height: 99vh;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.spot-selector {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 999;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  width: 200px;
  transition: all 0.3s ease;
}
.main-spot {
  padding: 12px 15px;
  font-weight: bold;
  color: #333;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
}

.main-spot:hover {
  background: #f5f5f5;
}

.arrow {
  font-size: 12px;
  transition: transform 0.3s;
}

.arrow.rotated {
  transform: rotate(180deg);
}

.sub-spots-wrapper {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.spot-selector.expanded .sub-spots-wrapper {
  max-height: 400px; /* 根据实际内容调整 */
  overflow-y: auto;
}

.sub-spot {
  padding: 10px 15px;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
}

.sub-spot:hover {
  background: #e6f7ff;
  color: #1890ff;
}

.sub-spot:not(:last-child) {
  border-bottom: 1px solid #f0f0f0;
}

/* 路线规划组件 */
.route-planner {
  flex: 1; /* 占 25% 宽度 */
  background: #ffffff;
  border-left: 1px solid #ddd;
  padding: 20px;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  display: flex;
  flex-direction: column;

  .planner-header {
    display: flex;
    justify-content: space-around;
    margin-bottom: 20px;

    button {
      flex: 1;
      padding: 10px;
      border: none;
      background: #f0f0f0;
      color: #333;
      font-size: 14px;
      font-weight: bold;
      border-radius: 4px;
      cursor: pointer;
      transition: background 0.3s, color 0.3s;
    }

    button.active {
      background: #1890ff;
      color: white;
    }

    button:not(:last-child) {
      margin-right: 10px;
    }

    button:hover {
      background: #e6f7ff;
      color: #1890ff;
    }
  }

  .planner-body {
    flex: 1;
    display: flex;
    flex-direction: column;

    .input-group {
      display: flex;
      align-items: center;
      margin-bottom: 15px;

      label {
        width: 50px;
        font-weight: bold;
        color: #555;
      }

      input, select {
        flex: 1;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
        transition: border-color 0.3s;
      }

      input:focus, select:focus {
        border-color: #1890ff;
        outline: none;
      }

      .waypoints {
        flex: 1;
        display: flex;
        flex-direction: column;

        .waypoint {
          display: flex;
          align-items: center;
          margin-bottom: 10px;

          input {
            flex: 1;
            margin-right: 10px;
          }

          button {
            padding: 5px 10px;
            background: #ff4d4f;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
          }

          button:hover {
            background: #ff7875;
          }
        }

        button {
          padding: 8px;
          background: #52c41a;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: background 0.3s;
        }

        button:hover {
          background: #73d13d;
        }
      }
    }

    .input-group.start-point select,
    .input-group.end-point select {
      width: 250px; /* 设置固定宽度 */
      flex: unset; /* 取消 flex 布局对宽度的影响 */
    }

    .input-group.waypoints select {
      width: 225px; /* 设置固定宽度 */
      flex: unset; /* 取消 flex 布局对宽度的影响 */
      padding: 8px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
      transition: border-color 0.3s;
    }

    .input-group.waypoints select:focus {
      border-color: #1890ff;
      outline: none;
    }

    .input-group.center-point select,
    .input-group select {
      width: 250px; /* 设置固定宽度 */
      flex: unset; /* 取消 flex 布局对宽度的影响 */
      padding: 8px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
      transition: border-color 0.3s;
    }

    .input-group select:focus {
      border-color: #1890ff;
      outline: none;
    }

    .plan-route-btn {
      width: 100%;
      padding: 12px;
      background: #1890ff;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 16px;
      font-weight: bold;
      transition: background 0.3s;
    }

    .plan-route-btn:hover {
      background: #40a9ff;
    }

    .query-btn {
      width: 100%;
      padding: 12px;
      background: #1890ff;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 16px;
      font-weight: bold;
      transition: background 0.3s;
    }

    .query-btn:hover {
      background: #40a9ff;
    }
  }
}
/* 景点详情 */
.spot-details {
  position: absolute;
  z-index: 999;
  max-width: 300px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.details-content {
  padding: 15px;
  position: relative;
}

.details-content h2 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
}

.details-content img {
  width: 100%;
  max-height: 150px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 10px;
}

.details-content p {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.close-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #999;
  padding: 0 5px;
}

.close-btn:hover {
  color: #333;
}
/* 类型图例 */
.map-legend {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(255,255,255,0.9);
  padding: 10px;
  border-radius: 4px;
  z-index: 999;
}
.legend-item {
  display: flex;
  align-items: center;
  margin: 5px 0;
}
.legend-marker {
  display: inline-block;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  text-align: center;
  line-height: 20px;
  margin-right: 8px;
  font-size: 12px;
}

/* 添加返回按钮样式 */
.back-button {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  z-index: 1000;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  .back-icon {
    margin-right: 5px;
    font-size: 18px;
  }
  
  &:hover {
    background: #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  }
}

</style>