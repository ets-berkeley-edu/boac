import type {NavigationGuardNext, RouteLocation} from 'vue-router'
import {useContextStore} from '@/stores/context'


const goToLogin = (to: RouteLocation, next: NavigationGuardNext) => {
  next({
    path: '/',
    query: {
      m: to.query.error,
      redirect: to.fullPath
    }
  })
}

export default {
  requiresAuthenticated: (to: RouteLocation, from: RouteLocation, next: NavigationGuardNext) => {
    if (useContextStore().currentUser.isAuthenticated) {
      next()
    } else {
      goToLogin(to, next)
    }
  }
}
