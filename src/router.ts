const Login = () => import('./layouts/Login.vue')
import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'

const routes:RouteRecordRaw[] = [
  {
    component: Login,
    path: '/',
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
