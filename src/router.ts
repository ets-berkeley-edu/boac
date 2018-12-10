import _ from 'lodash';
import Admin from '@/views/Admin.vue';
import AllCohorts from '@/views/cohort/AllCohorts.vue';
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
import { getAppConfig } from '@/api/config';
import { getUserProfile, getUserStatus } from '@/api/user';

Vue.use(Router);

const redirect = (path: string, params: any) => {
  for (const key in params) {
    path = _.replace(path, ':' + key, params[key]);
  }
  window.location.href = store.state.apiBaseUrl + path;
};

const lazyInitConfig = callback => {
  const config = store.getters.config;
  if (config) {
    return callback(config);
  } else {
    return getAppConfig().then(config => {
      store.commit('storeConfig', config);
      callback(config);
    });
  }
};

const lazyInitUserStatus = callback => {
  const isAuthenticated = store.getters.isUserAuthenticated;
  if (isAuthenticated === null) {
    return getUserStatus().then(data => {
      if (data.isAuthenticated) {
        store.commit('userAuthenticated');
        callback(true);
      } else {
        callback(false);
      }
    });
  } else {
    return callback(isAuthenticated);
  }
};

const lazyInitUserProfile = callback => {
  const user = store.getters.user;
  if (user) {
    return callback(user);
  } else {
    return getUserProfile().then(user => {
      store.commit('registerUser', user);
      callback(user);
    });
  }
};

const requiresAuth = (to: any, from: any, next: any) => {
  lazyInitUserStatus(isAuthenticated => {
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
        lazyInitUserStatus(isAuthenticated => {
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
    lazyInitConfig(() => {
      next();
    });
  }
});

router.afterEach((to: any) => {
  let name = _.get(to, 'meta.title') || _.capitalize(to.name) || 'Welcome';
  document.title = `${name} | BOAC`;
  lazyInitUserStatus(isAuthenticated => {
    if (isAuthenticated) {
      lazyInitUserProfile(() => {
        return;
      });
    }
  });
});

export default router;
