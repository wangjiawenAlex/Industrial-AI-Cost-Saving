<template>
  <!-- 查询历史 -->
  <div class="sidebar-section history-section">
    <div class="section-header">
      <span>📋 查询历史</span>
      <span class="section-sub">History Records</span>
    </div>
    
    <div v-if="history.length === 0" class="no-history">
      暂无查询历史
    </div>
    
    <div v-else class="history-list">
      <div 
        v-for="(item, index) in history.slice(0, 5)" 
        :key="index"
        class="history-item"
        @click="$emit('viewHistory', item)"
      >
        <div class="history-order">📝 订单 {{ item.order_id }}</div>
        <div class="history-time">{{ item.timestamp }}</div>
      </div>
    </div>

    <el-button class="logout-btn" @click="$emit('logout')">
      🚪 退出登录
    </el-button>
  </div>

  <!-- 查询示例 -->
  <div class="sidebar-section">
    <div class="section-title">💡 查询示例</div>
    <div class="example-list">
      <div class="example-item">• 查询订单 4200000001 的状态</div>
      <div class="example-item">• 我的订单 4200000002 怎么样了</div>
      <div class="example-item">• 订单号 4200000003 完成了吗</div>
      <div class="example-item">• 帮我查一下订单 4200000004</div>
    </div>
  </div>

  <!-- 系统信息 -->
  <div class="sidebar-section">
    <div class="section-title">ℹ️ 系统信息</div>
    <div class="system-info">
      <div class="info-item">✅ 实时查询 SAP 系统</div>
      <div class="info-item">✅ 自然语言理解</div>
      <div class="info-item">✅ 智能订单匹配</div>
      <div class="info-item">✅ 历史记录保存</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  history: {
    type: Array,
    default: () => []
  }
})

defineEmits(['viewHistory', 'logout'])
</script>

<style scoped>
.sidebar-section {
  background: rgba(255,255,255,0.95);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
  color: #333;
}

.section-sub {
  font-size: 0.75rem;
  color: #999;
  font-weight: normal;
}

.section-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  font-size: 0.95rem;
}

.no-history {
  text-align: center;
  color: #999;
  padding: 20px 0;
  font-size: 0.9rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  background: rgba(255,255,255,0.2);
  border-radius: 8px;
  padding: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.history-item:hover {
  background: rgba(255,255,255,0.3);
  transform: translateX(4px);
}

.history-order {
  font-weight: 500;
  color: #333;
  font-size: 0.9rem;
}

.history-time {
  font-size: 0.75rem;
  color: #999;
  margin-top: 4px;
}

.logout-btn {
  width: 100%;
  border-radius: 8px;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
  border: none;
  color: white;
  font-weight: 500;
}

.logout-btn:hover {
  opacity: 0.9;
}

.example-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.example-item {
  font-size: 0.85rem;
  color: #666;
  line-height: 1.5;
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  font-size: 0.85rem;
  color: #43a047;
}
</style>
