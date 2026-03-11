<template>
    <div class="map-wrapper">
      <!-- 地图容器 -->
      <div id="map-container" ref="mapContainer"></div>
      
      <!-- 控制按钮 -->
      <div class="map-controls">
        <el-button @click="handleResetView">重置视图</el-button>
        <el-button @click="handleAddMarker">添加标记</el-button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted } from 'vue';
  import { loadAMap } from '@/utils/amapLoader';
  
  // 地图实例
  const map = ref(null);
  const mapContainer = ref(null);
  
  // 初始化地图
  const initMap = async () => {
    try {
      const AMap = await loadAMap();
      
      map.value = new AMap.Map(mapContainer.value, {
        viewMode: '2D',
        zoom: 15,
        center: [116.397428, 39.90923], // 默认中心点（天安门）
      });
  
      // 添加默认控件
      map.value.addControl(new AMap.ControlBar({
        showZoomBar: true,
        showControlButton: true,
      }));
      
    } catch (error) {
      console.error('地图初始化失败:', error);
      ElMessage.error('地图加载失败，请刷新重试');
    }
  };
  
  // 重置视图
  const handleResetView = () => {
    map.value?.setZoomAndCenter(15, [116.397428, 39.90923]);
  };
  
  // 添加标记点
  const handleAddMarker = () => {
    if (!map.value) return;
    
    const marker = new AMap.Marker({
      position: map.value.getCenter(),
      title: '新标记点',
    });
    map.value.add(marker);
  };
  
  // 生命周期
  onMounted(initMap);
  onUnmounted(() => {
    map.value?.destroy(); // 销毁地图
  });
  </script>
  
  <style scoped>
  .map-wrapper {
    position: relative;
    width: 100%;
    height: 600px;
  }
  
  #map-container {
    width: 100%;
    height: 100%;
  }
  
  .map-controls {
    position: absolute;
    top: 20px;
    right: 20px;
    z-index: 999;
  }
  </style>