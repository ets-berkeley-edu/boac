import _ from 'lodash';
import Admin from '@/views/Admin.vue';
import AllCohorts from '@/views/AllCohorts.vue';
import Cohort from '@/views/Cohort.vue';
import Course from '@/views/Course.vue';
import CuratedGroup from '@/views/CuratedGroup.vue';
import Home from '@/views/Home.vue';
import Login from '@/layouts/Login.vue';
import NotFound from '@/views/NotFound.vue';
import Router from 'vue-router';
import Search from '@/views/Search.vue';
import StandardLayout from './layouts/StandardLayout.vue';
import store from '@/store';
import Student from '@/views/Student.vue';
import Vue from 'vue';

Vue.use(Router);

const requiresAuth = (to: any, from: any, next: any) => {
  store.dispatch('user/loadUserStatus').then(isAuthenticated => {
    if (isAuthenticated) {
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
        store.dispatch('user/loadUserStatus').then(isAuthenticated => {
          if (isAuthenticated) {
            next(to.query.redirect || '/home');
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
      component: StandardLayout,
      beforeEnter: requiresAuth,
      children: [
        {
          path: '/home',
          name: 'home',
          component: Home,
          meta: {
            title: 'Home'
          }
        },
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
          path: '/curated_group/:id',
          component: CuratedGroup,
          props: true,
          meta: {
            title: 'Curated Group'
          }
        },
        {
          path: '/student/:uid',
          component: Student,
          meta: {
            title: 'Student'
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
  store.dispatch('context/loadConfig').then(() => {
    store.dispatch('context/clearErrorsInStore').then(() => next());
  });
});

router.afterEach((to: any) => {
  let name = _.get(to, 'meta.title') || _.capitalize(to.name) || 'Welcome';
  document.title = `${name} | BOAC`;
  if (to.query.error) {
    store.dispatch('context/reportError', {
      message: to.query.error
    });
  }
  store.dispatch('user/loadUserStatus').then(isAuthenticated => {
    if (isAuthenticated) {
      store.dispatch('user/loadUser').then(() => {
        store.dispatch('cohort/loadMyCohorts');
        store.dispatch('curated/loadMyCuratedGroups');
        return;
      });
    }
  });
});

export default router;
