import _ from 'lodash';
import Admin from '@/views/Admin.vue';
import AllCohorts from '@/views/AllCohorts.vue';
import AllGroups from '@/views/AllGroups.vue';
import Cohort from '@/views/Cohort.vue';
import Course from '@/views/Course.vue';
import CreateCuratedGroup from '@/views/CreateCuratedGroup.vue'
import CuratedGroup from '@/views/CuratedGroup.vue';
import DropInDesk from '@/layouts/DropInDesk.vue';
import DropInWaitlist from '@/views/DropInWaitlist.vue';
import Home from '@/views/Home.vue';
import Login from '@/layouts/Login.vue';
import NotFound from '@/views/NotFound.vue';
import Router from 'vue-router';
import Search from '@/views/Search.vue';
import StandardLayout from '@/layouts/StandardLayout.vue';
import store from '@/store';
import Student from '@/views/Student.vue';
import Vue from 'vue';

Vue.use(Router);

const isAdvisor = user => {
  return !!_.size(_.filter(user.departments, d => d.isAdvisor || d.isDirector));
};

const isScheduler = user => {
  return !!_.size(_.filter(user.departments, d => d.isScheduler));
};

const requiresAuth = (to: any, from: any, next: any) => {
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
};

const requiresAdvisor = (to: any, from: any, next: any) => {
  store.dispatch('user/loadUser').then(data => {
    if (data.isAuthenticated) {
      store.dispatch('user/loadUser').then(user => {
        if (isAdvisor(user) || user.isAdmin) {
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
  });
};

const requiresScheduler = (to: any, from: any, next: any) => {
  store.dispatch('user/loadUser').then(data => {
    if (store.getters['context/featureFlagAppointments']) {
      if (data.isAuthenticated) {
        store.dispatch('user/loadUser').then(user => {
          if (isScheduler(user) || user.isAdmin) {
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
};

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/login',
      component: Login,
      beforeEnter: (to: any, from: any, next: any) => {
        store.dispatch('user/loadUser').then(user => {
          if (user.isAuthenticated) {
            if (isAdvisor(user) || user.isAdmin) {
              next(to.query.redirect || '/home');
            } else if (isScheduler(user)) {
              next({ path: '/appt/desk' });
            } else {
              next({ path: '/404' });
            }
          } else {
            next();
          }
        });
      },
      meta: {
        title: 'Welcome'
      }
    },
    {
      path: '/',
      component: DropInDesk,
      beforeEnter: requiresScheduler,
      children: [
        {
          path: '/appt/desk',
          name: 'apptDesk',
          component: DropInWaitlist,
          meta: {
            title: 'Drop-in Appointments Desk'
          }
        }
      ]
    },
    {
      path: '/',
      component: StandardLayout,
      beforeEnter: requiresAdvisor,
      children: [
        {
          path: '/admin',
          name: 'admin',
          component: Admin,
          meta: {
            title: 'Admin'
          }
        },
        {
          path: '/cohorts/all',
          component: AllCohorts,
          meta: {
            title: 'All Cohorts'
          }
        },
        {
          path: '/cohort/:id',
          component: Cohort,
          meta: {
            title: 'Cohort'
          }
        },
        {
          path: '/course/:termId/:sectionId',
          component: Course,
          meta: {
            title: 'Course'
          }
        },
        {
          path: '/curated/:id',
          component: CuratedGroup,
          props: true,
          meta: {
            title: 'Curated Group'
          }
        },
        {
          path: '/curate',
          component: CreateCuratedGroup,
          props: true,
          meta: {
            title: 'Create Curated Group'
          }
        },
        {
          path: '/groups/all',
          component: AllGroups,
          meta: {
            title: 'All Groups'
          }
        },
        {
          path: '/search',
          component: Search,
          meta: {
            title: 'Search'
          }
        },
        {
          path: '/student/:uid',
          component: Student,
          meta: {
            title: 'Student'
          }
        }
      ]
    },
    {
      path: '/',
      component: StandardLayout,
      beforeEnter: requiresAuth,
      children: [
        {
          beforeEnter: (to: any, from: any, next: any) => {
            store.dispatch('user/loadUser').then(user => {
              if (isScheduler(user) && !isAdvisor(user) && !user.isAdmin) {
                next({ path: '/appt/desk' });
              } else {
                next();
              }
            });
          },
          path: '/home',
          name: 'home',
          component: Home,
          meta: {
            title: 'Home'
          }
        },
        {
          path: '/404',
          component: NotFound,
          meta: {
            title: 'Page not found'
          }
        },
        {
          path: '*',
          redirect: '/404'
        }
      ]
    }
  ]
});

router.beforeEach((to: any, from: any, next: any) => {
  store.dispatch('context/clearAlertsInStore').then(() => next());
});

router.afterEach((to: any) => {
  let name = _.get(to, 'meta.title') || _.capitalize(to.name) || 'Welcome';
  document.title = `${name} | BOA`;
  if (to.query.error) {
    store.dispatch('context/reportError', {
      message: to.query.error
    });
  }
});

export default router;
