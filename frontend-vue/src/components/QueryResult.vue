<template>
  <div v-if="result" class="result-section">
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-label">📦 订单号</div>
        <div class="metric-value">{{ result.order_id }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">📊 订单状态</div>
        <div class="metric-value">
          <span :class="['status-tag', getStatusClass(result.status)]">
            {{ result.status }}
          </span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-label">🆔 查询 ID</div>
        <div class="metric-value">{{ result.log_id }}</div>
      </div>
    </div>

    <div class="ai-response">
      <div class="ai-response-title">🤖 AI 助手回复</div>
      <div class="ai-response-content" v-html="formatResponse(result.response)"></div>
    </div>
  </div>
  <div v-else class="no-result">
    <div class="no-result-icon">📋</div>
    <div class="no-result-text">输入订单号或描述查询内容，获取订单状态</div>
  </div>
</template>

<script setup>
defineProps({
  result: {
    type: Object,
    default: null
  }
})

const formatResponse = (text) => {
  if (!text) return ''
  return text.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
}

const getStatusClass = (status) => {
  const statusMap = {
    '制作中': 'status-making',
    '已完成': 'status-completed',
    '已发货': 'status-shipped',
    '已取消': 'status-cancelled',
    '待付款': 'status-pending',
    '运输中': 'status-transit',
    '退款中': 'status-refund'
  }
  return statusMap[status] || 'status-default'
}
</script>

<style scoped>
.result-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-top: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.metrics-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.metric-card {
  flex: 1;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.metric-label {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.ai-response {
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #91d5ff;
}

.ai-response-title {
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 12px;
}

.ai-response-content {
  line-height: 1.8;
  color: #333;
}

.ai-response-content :deep(strong) {
  color: #1890ff;
}

/* 状态标签 */
.status-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.status-making {
  background: #fff3e0;
  color: #f57c00;
}

.status-completed {
  background: #e8f5e9;
  color: #43a047;
}

.status-shipped {
  background: #e3f2fd;
  color: #1976d2;
}

.status-cancelled {
  background: #ffebee;
  color: #e53935;
}

.status-pending {
  background: #fce4ec;
  color: #d81b60;
}

.status-transit {
  background: #f3e5f5;
  color: #8e24aa;
}

.status-refund {
  background: #fff8e1;
  color: #ff8f00;
}

.status-default {
  background: #f5f5f5;
  color: #757575;
}

.no-result {
  background: white;
  border-radius: 16px;
  padding: 60px 24px;
  margin-top: 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.no-result-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.no-result-text {
  color: #999;
  font-size: 0.95rem;
}
</style>
