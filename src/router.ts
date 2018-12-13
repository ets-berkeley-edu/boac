import _ from 'lodash';
import Admin from '@/views/Admin.vue';
import AllCohorts from '@/views/cohort/AllCohorts.vue';
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

const redirect = (path: string, params: any) => {
  for (const key in params) {
    path = _.replace(path, ':' + key, params[key]);
  }
  window.location.href = store.getters.apiBaseUrl + path;
};

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
          beforeEnter: requiresAuth
        },
        {
          path: '/admin',
          name: 'admin',
          component: Admin,
          beforeEnter: requiresAuth
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
          beforeEnter: requiresAuth,
          meta: {
            legacyPathRedirect: '/cohort/filtered?id=:id',
            title: 'Cohort'
          }
        },
        {
          path: '/cohort/create',
          beforeEnter: requiresAuth,
          meta: {
            legacyPathRedirect: '/cohort/filtered',
            title: 'Create Cohort'
          }
        },
        {
          path: '/course/:termId/:sectionId',
          beforeEnter: requiresAuth,
          component: Course,
          meta: {
            legacyPathRedirect: '/course/:termId/:sectionId',
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
          component: Student
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
          path: '*',
          component: NotFound,
          beforeEnter: requiresAuth
        }
      ]
    }
  ]
});

router.beforeEach((to: any, from: any, next: any) => {
  let redirectPath =
    store.getters.legacyRedirectsEnabled &&
    _.get(to, 'meta.legacyPathRedirect');
  if (redirectPath) {
    redirect(redirectPath, to.params);
  } else {
    store.dispatch('context/loadConfig').then(() => {
      next();
    });
  }
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
