import Admin from '@/views/Admin.vue';
import AllCohorts from '@/views/cohort/AllCohorts.vue';
import Login from '@/views/Login.vue';
import CuratedGroup from '@/views/group/CuratedGroup.vue';
import ParentRoute from '@/views/ParentRoute.vue';
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
      path: '/cohort',
      component: ParentRoute,
      beforeEnter: requiresAuth,
      children: [
        {
          path: 'curated',
          component: ParentRoute,
          children: [
            {
              path: ':id',
              component: CuratedGroup,
              meta: { underConstruction: true }
            }
          ]
        },
        {
          path: 'filtered',
          meta: { underConstruction: true },
          component: ParentRoute,
          children: [
            {
              path: 'all',
              component: AllCohorts
            }
          ]
        }
      ]
    }
  ]
});

router.beforeEach(beforeEach);

export default router;
