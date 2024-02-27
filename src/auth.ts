import _ from 'lodash'
import {useContextStore} from '@/stores/context'

const goToLogin = (to: any, next: any) => {
  next({
    path: '/',
    query: {
      m: to.query.error,
      redirect: to.fullPath
    }
  })
}

export default {
  requiresAuthenticated: (to: any, from: any, next: any) => {
    if (_.get(useContextStore().currentUser, 'isAuthenticated')) {
      next()
    } else {
      goToLogin(to, next)
    }
  }
}
