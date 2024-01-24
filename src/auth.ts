import _ from 'lodash'
import store from '@/store'

const $_goToLogin = (to: any, next: any) => {
  next({
    path: '/login',
    query: {
      error: to.query.error,
      redirect: to.name === 'Home' ? undefined : to.fullPath
    }
  })
}

const isAdvisor = user => !!_.size(_.filter(user.departments, d => d.role === 'advisor'))

const isCE3 = user => !!_.size(_.filter(user.departments, d => d.code === 'ZCEEE' && _.includes(['advisor', 'director'], d.role)))

const isCoe = user => !!_.size(_.filter(user.departments, d => d.code === 'COENG' && _.includes(['advisor', 'director'], d.role)))

const isDirector = user => !!_.size(_.filter(user.departments, d => d.role === 'director'))

export default {
  isAdvisor,
  isCE3,
  isCoe,
  isDirector,
  requiresAdmin: (to: any, from: any, next: any) => {
    const currentUser = store.getters['context/currentUser']
    if (currentUser.isAuthenticated) {
      if (currentUser.isAdmin) {
        next()
      } else {
        next({path: '/404'})
      }
    } else {
      $_goToLogin(to, next)
    }
  },
  requiresAdvisor: (to: any, from: any, next: any) => {
    const currentUser = store.getters['context/currentUser']
    if (currentUser.isAuthenticated) {
      if (isAdvisor(currentUser) || isDirector(currentUser) || currentUser.isAdmin) {
        next()
      } else {
        next({path: '/404'})
      }
    } else {
      $_goToLogin(to, next)
    }
  },
  requiresAuthenticated: (to: any, from: any, next: any) => {
    if (store.getters['context/currentUser'].isAuthenticated) {
      next()
    } else {
      $_goToLogin(to, next)
    }
  },
  requiresCE3: (to: any, from: any, next: any) => {
    const currentUser = store.getters['context/currentUser']
    if (currentUser.isAuthenticated) {
      if (currentUser.isAdmin || isCE3(currentUser)) {
        next()
      } else {
        next({path: '/404'})
      }
    } else {
      $_goToLogin(to, next)
    }
  },
  requiresDegreeProgressPerm: (to: any, from: any, next: any) => {
    const currentUser = store.getters['context/currentUser']
    if (currentUser.canReadDegreeProgress) {
      next()
    } else if (currentUser.isAuthenticated) {
      next({path: '/404'})
    } else {
      $_goToLogin(to, next)
    }
  },
  requiresDirector: (to: any, from: any, next: any) => {
    const currentUser = store.getters['context/currentUser']
    if (currentUser.isAuthenticated) {
      if (isDirector(currentUser) || currentUser.isAdmin) {
        next()
      } else {
        next({path: '/404'})
      }
    } else {
      $_goToLogin(to, next)
    }
  }
}
