import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref(localStorage.getItem('token') || '')
  const userId = ref(localStorage.getItem('user_id') || null)
  const username = ref(localStorage.getItem('username') || '')
  const queryHistory = ref(JSON.parse(localStorage.getItem('query_history') || '[]'))

  // Getters
  const isLoggedIn = computed(() => !!token.value)

  // Actions
  function setUser(userData) {
    token.value = userData.token
    userId.value = userData.user_id
    username.value = userData.username
    
    // 持久化到 localStorage
    localStorage.setItem('token', userData.token)
    localStorage.setItem('user_id', String(userData.user_id))
    localStorage.setItem('username', userData.username)
  }

  function addQueryHistory(item) {
    queryHistory.value.unshift(item)
    // 只保留最近 20 条
    if (queryHistory.value.length > 20) {
      queryHistory.value = queryHistory.value.slice(0, 20)
    }
    localStorage.setItem('query_history', JSON.stringify(queryHistory.value))
  }

  function clearQueryHistory() {
    queryHistory.value = []
    localStorage.removeItem('query_history')
  }

  function logout() {
    token.value = ''
    userId.value = null
    username.value = ''
    queryHistory.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('username')
    localStorage.removeItem('query_history')
  }

  return {
    token,
    userId,
    username,
    queryHistory,
    isLoggedIn,
    setUser,
    addQueryHistory,
    clearQueryHistory,
    logout
  }
})
