/**
 * 动态加载高德地图API
 * @returns {Promise<window.AMap>}
 */
export const loadAMap = () => {
    return new Promise((resolve, reject) => {
      // 避免重复加载
      if (window.AMap) {
        console.log('高德地图API已加载，直接使用');
        return resolve(window.AMap);
      }
  
      // 创建script标签
      const script = document.createElement('script');
      script.src = `https://webapi.amap.com/maps?v=2.0&key=${import.meta.env.VITE_AMAP_KEY || '你的默认Key'}&plugin=AMap.Driving,AMap.MarkerClusterer`;
      script.async = true;
      script.defer = true;
      
      // 成功回调
      script.onload = () => {
        console.log('高德地图API加载成功');
        resolve(window.AMap);
      };
  
      // 失败回调
      script.onerror = (err) => {
        console.error('高德地图API加载失败', err);
        reject(new Error('高德地图加载失败'));
      };
  
      // 插入到DOM
      document.head.appendChild(script);
    });
  };