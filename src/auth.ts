import _ from 'lodash';
import store from "@/store";

const $_goToLogin = (to: any, next: any) => {
  next({
    path: '/login',
    query: {
      error: to.query.error,
      redirect: to.name === 'home' ? undefined : to.fullPath
    }
  });
};

const $_requiresScheduler = (to: any, next: any, authorizedDeptCodes: string[]) => {
  if (authorizedDeptCodes.length) {
    if (to.params.deptCode) {
      if (_.includes(authorizedDeptCodes, to.params.deptCode.toUpperCase())) {
        next();
      } else {
        next({ path: '/404' });
      }
    } else {
      // URL path has no dept code; Drop-in Advisor or Scheduler can proceed.
      next();
    }
  } else {
     next({ path: '/404' });
  }
};

const isAdvisor = user => !!_.size(_.filter(user.departments, d => d.isAdvisor || d.isDirector));

const getSchedulerDeptCodes = user =>  _.map(_.filter(user.departments, d => d.isScheduler), 'code');

export default {
  getSchedulerDeptCodes,
  isAdvisor,
  requiresAdmin: (to: any, from: any, next: any) => {
    store.dispatch('user/loadUser').then(user => {
      if (user.isAuthenticated) {
        if (user.isAdmin) {
          next();
        } else {
          next({ path: '/404' });
        }
      } else {
        $_goToLogin(to, next);
      }
    });
  },
  requiresAdvisor: (to: any, from: any, next: any) => {
    store.dispatch('user/loadUser').then(user => {
      if (user.isAuthenticated) {
        if (isAdvisor(user) || user.isAdmin) {
          next();
        } else {
          next({ path: '/404' });
        }
      } else {
        $_goToLogin(to, next);
      }
    });
  },
  requiresAuthenticated: (to: any, from: any, next: any) => {
    store.dispatch('user/loadUser').then(data => {
      if (data.isAuthenticated) {
        next();
      } else {
        $_goToLogin(to, next);
      }
    });
  },
  requiresDropInAdvisor: (to: any, from: any, next: any) => {
    store.dispatch('user/loadUser').then(user => {
      if (user.isAuthenticated) {
        if (user.isAdmin) {
          next();
        } else {
          $_requiresScheduler(to, next, _.map(user.dropInAdvisorStatus, 'deptCode'));
        }
      } else {
        $_goToLogin(to, next);
      }
    });
  },
  requiresScheduler: (to: any, from: any, next: any) => {
    store.dispatch('user/loadUser').then(user => {
      if (user.isAuthenticated) {
        if (user.isAdmin) {
          next();
        } else {
          $_requiresScheduler(to, next, getSchedulerDeptCodes(user));
        }
      } else {
        $_goToLogin(to, next);
      }
    });
  }
};
