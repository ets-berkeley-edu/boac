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

const redirect = (path: string, params: any) => {
  for (const key in params) {
    path = _.replace(path, ':' + key, params[key]);
  }
  window.location.href = store.getters['context/apiBaseUrl'] + path;
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
      },
      meta: {
        legacyPathRedirect: '/login'
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
            legacyPathRedirect: '/home',
            title: 'Home'
          }
        },
        {
          path: '/admin',
          name: 'admin',
          component: Admin,
          beforeEnter: requiresAuth,
          meta: {
            legacyPathRedirect: '/admin',
            title: 'Admin'
          }
        },
        {
          path: '/cohorts/all',
          component: AllCohorts,
          beforeEnter: requiresAuth,
          meta: {
            legacyPathRedirect: '/cohorts/all',
            title: 'All Cohorts'
          }
        },
        {
          path: '/cohort/:id',
          component: Cohort,
          beforeEnter: requiresAuth,
          meta: {
            legacyPathRedirect: '/cohort/filtered?id=:id',
            title: 'Cohort'
          }
        },
        {
          path: '/create_cohort',
          component: Cohort,
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
            legacyPathRedirect: '/cohort/curated/:id',
            title: 'Curated Group'
          }
        },
        {
          path: '/student/:uid',
          beforeEnter: requiresAuth,
          component: Student,
          meta: {
            legacyPathRedirect: '/student/:uid',
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
    let redirectPath =
      store.getters['context/legacyRedirectsEnabled'] &&
      _.get(to, 'meta.legacyPathRedirect');
    if (redirectPath) {
      let match = false;
      let vuePaths = store.getters['context/vuePaths'];
      _.each(vuePaths, vuePath => {
        // If the route matches a Vue-enabled path then DO NOT redirect. To determine a match we get regex that is
        // deduced from target string in VUE_PATHS config. Those "target strings" may contain '\1' and '\2' and we assume
        // those placeholders are numeric (eg, student UID). We hope this programmatic deduction works in all cases.
        vuePath = vuePath.replace(/\\1/g, '[0-9]+').replace(/\\2/g, '[0-9]+');
        if (new RegExp(`${vuePath}.*`).exec(to.fullPath)) {
          match = true;
          return false;
        }
      });
      if (match) {
        next();
      } else {
        redirect(redirectPath, to.params);
      }
    } else {
      next();
    }
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
