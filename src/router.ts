import _ from 'lodash';
import Admin from '@/views/Admin.vue';
import AllCohorts from '@/views/cohort/AllCohorts.vue';
import CuratedGroup from '@/views/group/CuratedGroup.vue';
import Home from '@/views/Home.vue';
import Router from 'vue-router';
import Search from '@/views/Search.vue';
import store from '@/store';
import Student from '@/views/Student.vue';
import Vue from 'vue';
import { getAppConfig } from '@/api/config';
import { getUserProfile } from '@/api/user';

Vue.use(Router);

const safeNext = (to: any, next: any) => {
  if (to.matched.length) {
    next();
  } else {
    next('/home');
  }
};

const redirect = (path: string, params: any) => {
  for (const key in params) {
    path = _.replace(path, ':' + key, params[key]);
  }
  window.location.href = store.state.apiBaseUrl + path;
};

const loadConfig = callback => {
  if (store.getters.config) {
    callback();
  } else {
    getAppConfig()
      .then(config => store.commit('storeConfig', config))
      .then(callback);
  }
};

const loadUserProfile = callback => {
  getUserProfile()
    .then(user => store.commit('registerUser', user))
    .then(callback);
};

const beforeEach = (to: any, from: any, next: any) => {
  let redirectPath = _.get(to, 'meta.legacyPathRedirect');
  if (redirectPath) {
    redirect(redirectPath, to.params);
  }
  loadConfig(() => {
    if (store.getters.user) {
      safeNext(to, next);
    } else {
      loadUserProfile(() => safeNext(to, next));
    }
  });
};

const requiresAuth = (to: any, from: any, next: any) => {
  return store.getters.user ? next() : next('/login');
};

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/login'
    },
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
      path: '/cohorts_all',
      component: AllCohorts,
      beforeEnter: requiresAuth,
      meta: {
        title: 'All Cohorts'
      }
    },
    {
      path: '/cohort_:id',
      beforeEnter: requiresAuth,
      meta: {
        legacyPathRedirect: '/cohort/filtered?id=:id',
        title: 'Cohort'
      }
    },
    {
      path: '/cohort_create',
      beforeEnter: requiresAuth,
      meta: {
        legacyPathRedirect: '/cohort/filtered',
        title: 'Create Cohort'
      }
    },
    {
      path: '/curated_group_:id',
      beforeEnter: requiresAuth,
      component: CuratedGroup,
      props: true,
      meta: {
        title: 'Curated Group'
      }
    },
    {
      path: '/student_:uid',
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
    }
  ]
});

router.beforeEach(beforeEach);

router.afterEach(to => {
  let name = _.get(to, 'meta.title') || _.capitalize(to.name) || 'Welcome';
  document.title = `${name} | BOAC`;
});

export default router;
