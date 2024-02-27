const Error = () => import('@/views/Error.vue')
const Login = () => import('./layouts/Login.vue')
const Home = () => import('@/views/Home.vue')
const NotFound = () => import('@/views/NotFound.vue')
const Profile = () => import('@/views/Profile.vue')
const StandardLayout = () => import('@/layouts/StandardLayout.vue')
import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'
import {isAdvisor, isDirector} from '@/berkeley'
import {trim} from 'lodash'
import {useContextStore} from '@/stores/context'

const $_goToLogin = (to: any, next: any) => {
  next({
    path: '/login',
    query: {
      error: to.query.error,
      redirect: to.name === 'Home' ? undefined : to.fullPath
    }
  })
}

const routes:RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    component: Login,
    path: '/login',
  },
  {
    path: '/login',
    component: Login,
    beforeEnter: (to: any, from: any, next: any) => {
      const currentUser = useContextStore().currentUser
      if (currentUser.isAuthenticated) {
        if (trim(to.query.redirect)) {
          next(to.query.redirect)
        } else if (isAdvisor(currentUser) || isDirector(currentUser) || currentUser.isAdmin) {
          next('/home')
        } else {
          next({path: '/404'})
        }
      } else {
        next()
      }
    },
    meta: {
      title: 'Welcome'
    }
  },
  {
    path: '/',
    component: StandardLayout,
    beforeEnter: (to: any, from: any, next: any) => {
      // Requires Authenticated
      if (useContextStore().currentUser.isAuthenticated) {
        next()
      } else {
        $_goToLogin(to, next)
      }
    },
    children: [
      {
        path: '/home',
        component: Home,
        name: 'Home'
      },
      {
        path: '/profile',
        component: Profile,
        name: 'Advisor Profile'
      },
      {
        path: '/error',
        component: Error,
        name: 'Error'
      },
      {
        path: '/404',
        component: NotFound,
        name: '404'
      },
      {
        path: '*',
        redirect: '/404',
        name: 'Page not found'
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
