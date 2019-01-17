import _ from 'lodash';
import Admin from '@/views/Admin.vue';
import AllCohorts from '@/views/cohort/AllCohorts.vue';
import Cohort from '@/views/cohort/Cohort.vue';
import Course from '@/views/Course.vue';
import CuratedGroup from '@/views/group/CuratedGroup.vue';
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
      next('/login');
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
            next('/home');
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
      children: [
        {
          path: '/home',
          name: 'home',
          component: Home,
          beforeEnter: requiresAuth,
          meta: {
            title: 'Home'
          }
        },
        {
          path: '/admin',
          name: 'admin',
          component: Admin,
          beforeEnter: requiresAuth,
          meta: {
            title: 'Admin'
          }
        },
        {
          path: '/cohorts/all',
          component: AllCohorts,
          beforeEnter: requiresAuth,
          meta: {
            title: 'All Cohorts'
          }
        },
        {
          path: '/cohort/:id',
          component: Cohort,
          beforeEnter: requiresAuth,
          meta: {
            title: 'Cohort'
          }
        },
        {
          path: '/create_cohort',
          component: Cohort,
          beforeEnter: requiresAuth,
          meta: {
            title: 'Create Cohort'
          }
        },
        {
          path: '/course/:termId/:sectionId',
          beforeEnter: requiresAuth,
          component: Course,
          meta: {
            title: 'Course'
          }
        },
        {
          path: '/curated_group/:id',
          beforeEnter: requiresAuth,
          component: CuratedGroup,
          props: true,
          meta: {
            title: 'Curated Group'
          }
        },
        {
          path: '/student/:uid',
          beforeEnter: requiresAuth,
          component: Student,
          meta: {
            title: 'Student'
          }
        },
        {
          path: '/search',
          beforeEnter: requiresAuth,
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
          component: NotFound,
          beforeEnter: requiresAuth
        }
      ]
    }
  ]
});

router.beforeEach((to: any, from: any, next: any) => {
  store.dispatch('context/loadConfig').then(() => {
    store.dispatch('context/clearErrors').then(() => next());
  });
});

router.afterEach((to: any) => {
  let name = _.get(to, 'meta.title') || _.capitalize(to.name) || 'Welcome';
  document.title = `${name} | BOAC`;
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
