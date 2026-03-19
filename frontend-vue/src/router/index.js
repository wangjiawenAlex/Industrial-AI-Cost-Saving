import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Query from '../views/Query.vue'

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

router.beforeEach((to, from, next) => {
  const userId = localStorage.getItem('user_id')
  if (to.meta.requiresAuth && !userId) {
    next('/')
  } else {
    next()
  }
})

export default router
