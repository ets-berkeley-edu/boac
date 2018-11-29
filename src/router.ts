import Admin from '@/views/Admin.vue';
import AllCohorts from '@/views/cohort/AllCohorts.vue';
import CuratedGroup from '@/views/group/CuratedGroup.vue';
import Login from '@/views/Login.vue';
import Search from '@/views/Search.vue';
import Student from '@/views/Student.vue';
import store from '@/store';
import Vue from 'vue';
import VueRouter from 'vue-router';
import { getAppConfig } from '@/api/config';
import { getUserProfile } from '@/api/user';

Vue.use(VueRouter);

let beforeEach = (to: any, from: any, next: any) => {
  let safeNext = (to: any, next: any) => {
    if (to.matched.length) {
      next();
    } else {
      next('/admin');
    }
  };
  if (store.getters.user) {
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

let requiresAuth = (to: any, from: any, next: any) => {
  if (store.getters.user) {
    next();
  } else {
    window.location = store.state.apiBaseUrl;
  }
};

const router = new VueRouter({
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
      component: AllCohorts
    },
    {
      path: '/curated_group_:id',
      beforeEnter: requiresAuth,
      component: CuratedGroup,
      meta: { legacyUri: '/cohort/curated/:id' }
    },
    {
      path: '/student_:uid',
      beforeEnter: requiresAuth,
      component: Student
    },
    {
      path: '/cohort_:id',
      beforeEnter: requiresAuth,
      meta: { legacyUri: '/cohort/filtered?id=:id' }
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
