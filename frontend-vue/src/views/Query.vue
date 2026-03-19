<template>
  <div class="query-page">
    <!-- Header -->
    <div class="schneider-header">
      <div class="header-left">
        <div class="logo-icon">SE</div>
        <div class="header-titles">
          <div class="header-title">Schneider Electric</div>
          <div class="header-subtitle">万高数据订单查询系统</div>
        </div>
      </div>
      <div class="header-right">
        <span>👋 欢迎, {{ username }}</span>
      </div>
    </div>

    <div class="main-container">
      <!-- Sidebar -->
      <div class="sidebar">
        <div class="history-header">
          <div class="history-title">📋 查询历史</div>
          <div class="history-subtitle">History Records</div>
        </div>
        
        <el-button type="danger" plain class="logout-btn" @click="handleLogout">
          🚪 退出登录
        </el-button>
        
        <el-divider />
        
        <div class="history-list" v-if="queryHistory.length">
          <el-collapse v-model="activeHistory">
            <el-collapse-item 
              v-for="(item, index) in queryHistory.slice(0, 15)" 
              :key="index"
              :name="index"
            >
              <template #title>
                <div class="history-item-title">
                  <span>📝 订单 {{ item.order_id }}</span>
                </div>
              </template>
              <div class="history-detail">
                <p><strong>🕒 时间:</strong> {{ item.timestamp }}</p>
                <p><strong>📦 订单号:</strong> {{ item.order_id }}</p>
                <p><strong>📊 状态:</strong> {{ item.status }}</p>
                <p><strong>❓ 查询:</strong> {{ item.query.substring(0, 50) }}...</p>
                <el-button size="small" type="primary" @click="viewDetail(item)">
                  🔍 查看详情
                </el-button>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
        <el-empty v-else description="暂无查询历史" :image-size="60" />
      </div>

      <!-- Main Content -->
      <div class="main-content">
        <!-- Query Card -->
        <div class="query-card">
          <div class="query-title">
            <div class="query-icon">🔍</div>
            <span>订单查询</span>
          </div>
          
          <el-input
            v-model="queryText"
            type="textarea"
            :rows="4"
            placeholder="例如:查询订单 4200000001 的状态&#10;或者:我想知道订单号 4200000002 现在怎么样了&#10;支持自然语言输入..."
            resize="none"
          />
          
          <el-button 
            type="primary" 
            class="query-btn"
            :loading="queryLoading"
            @click="handleQuery"
          >
            开始查询
          </el-button>

          <!-- Results -->
          <div v-if="currentResponse" class="result-section">
            <el-divider />
            
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="metric-card">
                  <div class="metric-label">📦 订单号</div>
                  <div class="metric-value">{{ currentResponse.order_id }}</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="metric-card">
                  <div class="metric-label">📊 订单状态</div>
                  <div class="metric-value">{{ currentResponse.status }}</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="metric-card">
                  <div class="metric-label">🆔 查询 ID</div>
                  <div class="metric-value">{{ currentResponse.log_id }}</div>
                </div>
              </el-col>
            </el-row>

            <div class="ai-response">
              <div class="ai-response-title">🤖 AI 助手回复</div>
              <div class="ai-response-content" v-html="formatResponse(currentResponse.response)"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Sidebar -->
      <div class="right-sidebar">
        <div class="example-box">
          <div class="example-title">💡 查询示例</div>
          <div class="example-item">• 查询订单 4200000001 的状态</div>
          <div class="example-item">• 我的订单 4200000002 怎么样了</div>
          <div class="example-item">• 订单号 4200000003 完成了吗</div>
          <div class="example-item">• 帮我查一下订单 4200000004</div>
        </div>

        <div class="info-box">
          <div class="info-title">ℹ️ 系统信息</div>
          <div class="info-item">✅ 实时查询 SAP 系统</div>
          <div class="info-item">✅ 自然语言理解</div>
          <div class="info-item">✅ 智能订单匹配</div>
          <div class="info-item">✅ 历史记录保存</div>
        </div>

        <div class="brand-box">
          <div class="brand-logo">SE</div>
          <div class="brand-text">Schneider Electric</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()

const username = ref('')
const queryText = ref('')
const queryLoading = ref(false)
const activeHistory = ref([])
const queryHistory = ref([])
const currentResponse = ref(null)

onMounted(() => {
  username.value = localStorage.getItem('username') || '用户'
  const history = localStorage.getItem('query_history')
  if (history) {
    queryHistory.value = JSON.parse(history)
  }
})

const handleLogout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('query_history')
  router.push('/')
}

const handleQuery = async () => {
  if (!queryText.value.trim()) {
    ElMessage.error('请输入查询内容')
    return
  }
  
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    ElMessage.error('请先登录')
    router.push('/')
    return
  }
  
  queryLoading.value = true
  try {
    const response = await axios.post('/api/query', {
      user_id: parseInt(userId),
      query_text: queryText.value
    })
    
    if (response.data.success) {
      const result = {
        timestamp: new Date().toLocaleString(),
        query: queryText.value,
        order_id: response.data.order_id,
        status: response.data.sap_status,
        response: response.data.final_response,
        log_id: response.data.log_id
      }
      
      currentResponse.value = result
      queryHistory.value.unshift(result)
      localStorage.setItem('query_history', JSON.stringify(queryHistory.value))
      
      ElMessage.success('查询成功')
    } else {
      ElMessage.error(`查询失败: ${response.data.message}`)
    }
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      ElMessage.error('无法连接到后端服务,请确保 FastAPI 服务已启动')
    } else {
      ElMessage.error(error.response?.data?.message || '查询异常')
    }
  } finally {
    queryLoading.value = false
  }
}

const viewDetail = (item) => {
  currentResponse.value = item
}

const formatResponse = (text) => {
  if (!text) return ''
  return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
}
</script>

<style scoped>
.query-page {
  min-height: 100vh;
  background: #f9fafb;
}

.schneider-header {
  background: linear-gradient(135deg, #3DCD58 0%, #2BA845 100%);
  padding: 20px 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4px 12px rgba(61, 205, 88, 0.2);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-icon {
  width: 50px;
  height: 50px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 24px;
  color: #3DCD58;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header-title {
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
}

.header-subtitle {
  color: rgba(255,255,255,0.9);
  font-size: 0.9rem;
}

.header-right {
  color: white;
  font-size: 1rem;
}

.main-container {
  display: flex;
  padding: 20px;
  gap: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

.sidebar {
  width: 280px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  height: fit-content;
  position: sticky;
  top: 20px;
}

.history-header {
  background: linear-gradient(135deg, #3DCD58, #2BA845);
  border-radius: 10px;
  padding: 15px;
  text-align: center;
  margin-bottom: 20px;
}

.history-title {
  color: white;
  font-size: 1.2rem;
  font-weight: 700;
}

.history-subtitle {
  color: rgba(255,255,255,0.9);
  font-size: 0.8rem;
  margin-top: 5px;
}

.logout-btn {
  width: 100%;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.history-item-title {
  font-size: 14px;
}

.history-detail {
  padding: 10px;
  font-size: 13px;
  color: #666;
}

.history-detail p {
  margin-bottom: 5px;
}

.main-content {
  flex: 1;
  min-width: 0;
}

.query-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
}

.query-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #626469;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.query-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #3DCD58, #2BA845);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}

.query-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #3DCD58 0%, #2BA845 100%);
  border: none;
  border-radius: 10px;
  margin-top: 20px;
  box-shadow: 0 4px 12px rgba(61, 205, 88, 0.3);
}

.query-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(61, 205, 88, 0.4);
}

.result-section {
  margin-top: 30px;
}

.metric-card {
  background: linear-gradient(135deg, #fff 0%, #f9fafb 100%);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 15px;
}

.metric-label {
  font-size: 0.85rem;
  color: #626469;
  font-weight: 500;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #3DCD58;
}

.ai-response {
  background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
  border-left: 4px solid #3DCD58;
  border-radius: 12px;
  padding: 24px;
  margin-top: 20px;
}

.ai-response-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #3DCD58;
  margin-bottom: 12px;
}

.ai-response-content {
  font-size: 1rem;
  color: #626469;
  line-height: 1.6;
}

.right-sidebar {
  width: 300px;
  flex-shrink: 0;
}

.example-box {
  background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
  border-radius: 12px;
  padding: 20px;
  border-left: 4px solid #FFD100;
  margin-bottom: 20px;
}

.example-title {
  font-size: 1rem;
  font-weight: 600;
  color: #E47F00;
  margin-bottom: 12px;
}

.example-item {
  font-size: 0.9rem;
  color: #626469;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.example-item:last-child {
  border-bottom: none;
}

.info-box {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 20px;
}

.info-title {
  font-size: 1rem;
  font-weight: 600;
  color: #626469;
  margin-bottom: 12px;
}

.info-item {
  font-size: 0.85rem;
  color: #626469;
  padding: 6px 0;
}

.brand-box {
  background: linear-gradient(135deg, #3DCD58 0%, #2BA845 100%);
  border-radius: 12px;
  padding: 24px;
  text-align: center;
}

.brand-logo {
  color: white;
  font-size: 2.5rem;
  font-weight: 800;
}

.brand-text {
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  margin-top: 5px;
}

/* Responsive */
@media (max-width: 1200px) {
  .right-sidebar {
    display: none;
  }
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
  
  .schneider-header {
    flex-direction: column;
    gap: 10px;
    padding: 15px;
  }
  
  .query-card {
    padding: 20px;
  }
}
</style>
