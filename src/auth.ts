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

const $_requiresScheduler = (to: any, next: any, authorizedDeptCodes: string[]) => {
  if (authorizedDeptCodes.length) {
    if (to.params.deptCode) {
      if (_.includes(authorizedDeptCodes, to.params.deptCode.toUpperCase())) {
        next()
      } else {
        next({path: '/404'})
      }
    } else {
      // URL path has no dept code; Drop-in Advisor or Scheduler can proceed.
      next()
    }
  } else {
     next({path: '/404'})
  }
}

const isAdvisor = user => !!_.size(_.filter(user.departments, d => d.role === 'advisor'))

const isCE3 = user => !!_.size(_.filter(user.departments, d => d.code === 'ZCEEE' && _.includes(['advisor', 'director'], d.role)))

const isCoe = user => !!_.size(_.filter(user.departments, d => d.code === 'COENG' && _.includes(['advisor', 'director'], d.role)))

const isDirector = user => !!_.size(_.filter(user.departments, d => d.role === 'director'))

const getSchedulerDeptCodes = user => _.map(_.filter(user.departments, d => d.role === 'scheduler'), 'code')

export default {
  getSchedulerDeptCodes,
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
  },
  requiresDropInAdvisor: (to: any, from: any, next: any) => {
    const currentUser = store.getters['context/currentUser']
    if (currentUser.isAuthenticated) {
      if (currentUser.isAdmin) {
        next()
      } else {
        $_requiresScheduler(to, next, _.map(currentUser.dropInAdvisorStatus, 'deptCode'))
      }
    } else {
      $_goToLogin(to, next)
    }
  },
  requiresScheduler: (to: any, from: any, next: any) => {
    const currentUser = store.getters['context/currentUser']
    if (currentUser.isAuthenticated) {
      if (currentUser.isAdmin) {
        next()
      } else {
        $_requiresScheduler(to, next, getSchedulerDeptCodes(store.getters['context/currentUser']))
      }
    } else {
      $_goToLogin(to, next)
    }
  }
}
