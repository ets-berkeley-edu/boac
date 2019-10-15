import _ from 'lodash';
import store from "@/store";

const isAdvisor = user => !!_.size(_.filter(user.departments, d => d.isAdvisor || d.isDirector));

const dropInAdvisorForDepartments = user =>  _.filter(user.departments, d => d.isDropInAdvisor);

const schedulerForDepartments = user =>  _.filter(user.departments, d => d.isScheduler);

export default {
  dropInAdvisorForDepartments,
  isAdvisor,
  requiresAdvisor: (to: any, from: any, next: any) => {
    store.dispatch('user/loadUser').then(user => {
      if (user.isAuthenticated) {
        if (isAdvisor(user) || user.isAdmin) {
          next();
        } else {
          next({ path: '/404' });
        }
      } else {
        next({
          path: '/login',
          query: {
            error: to.query.error,
            redirect: to.name === 'home' ? undefined : to.fullPath
          }
        });
      }
    });
  },
  requiresAuthenticated: (to: any, from: any, next: any) => {
    store.dispatch('user/loadUser').then(data => {
      if (data.isAuthenticated) {
        next();
      } else {
        next({
          path: '/login',
          query: {
            error: to.query.error,
            redirect: to.name === 'home' ? undefined : to.fullPath
          }
        });
      }
    });
  },
  requiresDropInAdvisor: (to: any, from: any, next: any) => {
    store.dispatch('user/loadUser').then(user => {
      if (store.getters['context/featureFlagAppointments']) {
        if (user.isAuthenticated) {
          if (_.size(dropInAdvisorForDepartments(user)) || user.isAdmin) {
            next();
          } else {
            next({ path: '/404' });
          }
        } else {
          next({
            path: '/login',
            query: {
              error: to.query.error,
              redirect: to.name === 'home' ? undefined : to.fullPath
            }
          });
        }
      } else {
         next({ path: '/404' });
      }
    });
  },
  requiresScheduler: (to: any, from: any, next: any) => {
    store.dispatch('user/loadUser').then(data => {
      if (store.getters['context/featureFlagAppointments']) {
        if (data.isAuthenticated) {
          store.dispatch('user/loadUser').then(user => {
            if (_.size(schedulerForDepartments(user)) || user.isAdmin) {
              next();
            } else {
              next({ path: '/404' });
            }
          });
        } else {
          next({
            path: '/login',
            query: {
              error: to.query.error,
              redirect: to.name === 'home' ? undefined : to.fullPath
            }
          });
        }
      } else {
         next({ path: '/404' });
      }
    });
  },
  schedulerForDepartments,
};
