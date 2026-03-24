import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Query from '../views/Query.vue'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/query',
    name: 'Query',
    component: Query,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 使用 Pinia store 判断登录状态
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
