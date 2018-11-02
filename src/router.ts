import Vue from 'vue';
import VueRouter from 'vue-router';
import store from '@/store';
import { getMyProfile } from '@/api/user';
import Login from '@/views/Login.vue';
import Home from '@/views/Home.vue';
import Admin from '@/views/Admin.vue';

Vue.use(VueRouter);

let beforeEach = (to: any, from: any, next: any) => {
  let safeNext = (to: any, next: any) => {
    if (to.matched.length) {
      next();
    } else {
      next('/home');
    }
  };
  if (store.getters.user) {
    safeNext(to, next);
  } else {
    getMyProfile().then(me => {
      if (me) {
        store.commit('registerMe', me);
      }
      safeNext(to, next);
    });
  }
};

let requiresAuth = (to: any, from: any, next: any) => {
  if (store.getters.user) {
    next();
  } else {
    next('/login');
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
          next('/home');
        } else {
          next();
        }
      }
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
    }
  ]
});

router.beforeEach(beforeEach);

export default router;
