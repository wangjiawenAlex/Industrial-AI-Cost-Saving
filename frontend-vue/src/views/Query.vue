<template>
  <div class="query-page">
    <!-- 顶部 Header -->
    <div class="schneider-header">
      <div class="header-logo">
        <div class="logo-icon">SE</div>
        <div class="header-titles">
          <div class="header-title">Schneider Electric</div>
          <div class="header-subtitle">万高数据订单查询系统</div>
        </div>
      </div>
      <div class="user-info">
        <span>👋 欢迎, {{ username }}</span>
      </div>
    </div>

    <div class="main-container">
      <!-- 左侧主内容 -->
      <div class="main-content">
        <!-- 查询卡片组件 -->
        <QueryCard 
          v-model="queryText"
          :loading="queryLoading"
          @query="queryLoading = true"
          @result="handleQueryResult"
        />

        <!-- 查询结果组件 -->
        <QueryResult :result="currentResponse" />
      </div>

      <!-- 右侧边栏组件 -->
      <div class="sidebar">
        <QuerySidebar 
          :history="queryHistory"
          @viewHistory="viewHistory"
          @logout="handleLogout"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import QueryCard from '@/components/QueryCard.vue'
import QueryResult from '@/components/QueryResult.vue'
import QuerySidebar from '@/components/QuerySidebar.vue'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const queryText = ref('')
const queryLoading = ref(false)
const queryHistory = ref([])
const currentResponse = ref(null)

// 从 Pinia store 初始化
onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/')
    return
  }
  
  username.value = userStore.username
  queryHistory.value = userStore.queryHistory
})

// 处理查询结果
const handleQueryResult = (result) => {
  queryLoading.value = false
  currentResponse.value = result
  userStore.addQueryHistory(result)
  queryHistory.value = userStore.queryHistory
}

// 查看历史记录
const viewHistory = (item) => {
  currentResponse.value = item
  queryText.value = item.query
}

// 退出登录
const handleLogout = () => {
  userStore.logout()
  router.push('/')
}
</script>

<style scoped>
.query-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}

.schneider-header {
  background: linear-gradient(135deg, #3DCD58 0%, #2BA845 100%);
  padding: 16px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: white;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #3DCD58;
  font-size: 1.1rem;
}

.header-titles {
  color: white;
}

.header-title {
  font-weight: 700;
  font-size: 1.2rem;
}

.header-subtitle {
  font-size: 0.8rem;
  opacity: 0.9;
}

.user-info {
  color: white;
  font-weight: 500;
}

.main-container {
  display: flex;
  gap: 24px;
  padding: 24px 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.main-content {
  flex: 1;
  min-width: 0;
}

.sidebar {
  width: 320px;
  flex-shrink: 0;
}

@media (max-width: 900px) {
  .main-container {
    flex-direction: column;
    padding: 16px;
  }
  
  .sidebar {
    width: 100%;
  }
}
</style>
