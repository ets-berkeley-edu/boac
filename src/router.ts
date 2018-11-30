import _ from 'lodash';
import Admin from '@/views/Admin.vue';
import AllCohorts from '@/views/cohort/AllCohorts.vue';
import CuratedGroup from '@/views/group/CuratedGroup.vue';
import Login from '@/views/Login.vue';
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
    window.location = store.state.apiBaseUrl;
  }
};

const beforeEach = (to: any, from: any, next: any) => {
  let legacyPathRedirect = _.get(to, 'meta.legacyPathRedirect');
  if (legacyPathRedirect) {
    for (const key in to.params) {
      legacyPathRedirect = _.replace(
        legacyPathRedirect,
        ':' + key,
        to.params[key]
      );
    }
    window.location = store.state.apiBaseUrl + legacyPathRedirect;
  } else if (store.getters.user) {
    safeNext(to, next);
  } else {
    getUserProfile().then(user => {
      if (user) {
        store.commit('registerUser', user);
        getAppConfig()
          .then(config => store.commit('storeConfig', config))
          .then(() => safeNext(to, next));
      } else {
        safeNext(to, next);
      }
    });
  }
};

const requiresAuth = (to: any, from: any, next: any) => {
  if (store.getters.user) {
    next();
  } else {
    window.location = store.state.apiBaseUrl;
  }
};

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
      beforeEnter: (to: any, from: any, next: any) => {
        if (store.getters.user) {
          next('/admin');
        } else {
          next();
        }
      }
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
      beforeEnter: requiresAuth
    },
    {
      path: '/cohort_:id',
      beforeEnter: requiresAuth,
      meta: { legacyPathRedirect: '/cohort/filtered?id=:id' }
    },
    {
      path: '/cohort_create',
      beforeEnter: requiresAuth,
      meta: { legacyPathRedirect: '/cohort/filtered' }
    },
    {
      path: '/curated_group_:id',
      beforeEnter: requiresAuth,
      component: CuratedGroup,
      meta: { legacyPathRedirect: '/cohort/curated/:id' }
    },
    {
      path: '/student_:uid',
      beforeEnter: requiresAuth,
      component: Student,
      meta: { legacyPathRedirect: '/student/:uid' }
    },
    {
      path: '/search',
      beforeEnter: requiresAuth,
      component: Search
    }
  ]
});

router.beforeEach(beforeEach);

export default router;
