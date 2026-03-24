<template>
  <div class="query-card">
    <div class="query-title">
      <div class="query-icon">🔍</div>
      <span>订单查询</span>
    </div>
    
    <el-input
      v-model="localQueryText"
      type="textarea"
      :rows="4"
      placeholder="例如:查询订单 4200000001 的状态
或者:我想知道订单号 4200000002 现在怎么样了
支持自然语言输入..."
      class="query-input"
      @keydown.enter.ctrl="handleQuery"
    />

    <el-button 
      type="primary" 
      class="query-btn"
      :loading="loading"
      @click="handleQuery"
    >
      开始查询
    </el-button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { queryOrder } from '@/api'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'query', 'result'])

const userStore = useUserStore()
const localQueryText = ref(props.modelValue)

watch(() => props.modelValue, (val) => {
  localQueryText.value = val
})

watch(localQueryText, (val) => {
  emit('update:modelValue', val)
})

const handleQuery = async () => {
  if (!localQueryText.value.trim()) {
    ElMessage.error('请输入查询内容')
    return
  }

  emit('query')
  
  try {
    const response = await queryOrder(userStore.userId, localQueryText.value)

    if (response.success) {
      const result = {
        timestamp: new Date().toLocaleString(),
        query: localQueryText.value,
        order_id: response.order_id,
        status: response.sap_status,
        response: response.final_response,
        log_id: response.log_id
      }
      
      emit('result', result)
      ElMessage.success('查询成功')
    } else {
      ElMessage.error(response.message || '查询失败')
    }
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      ElMessage.error('无法连接到后端服务')
    } else {
      ElMessage.error(error.message || '查询异常')
    }
  }
}
</script>

<style scoped>
.query-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.query-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.query-icon {
  font-size: 1.4rem;
}

.query-input :deep(.el-textarea__inner) {
  border-radius: 12px;
  font-size: 1rem;
  padding: 12px;
}

.query-btn {
  width: 100%;
  height: 48px;
  margin-top: 16px;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  background: linear-gradient(135deg, #3DCD58 0%, #2BA845 100%);
  border: none;
}

.query-btn:hover {
  opacity: 0.9;
}
</style>
