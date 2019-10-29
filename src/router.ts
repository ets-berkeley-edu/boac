import _ from 'lodash';
import Admin from '@/views/Admin.vue';
import AllCohorts from '@/views/AllCohorts.vue';
import AllGroups from '@/views/AllGroups.vue';
import AppointmentDropIn from '@/layouts/AppointmentDropIn.vue';
import auth from './auth';
import Cohort from '@/views/Cohort.vue';
import Course from '@/views/Course.vue';
import CreateCuratedGroup from '@/views/CreateCuratedGroup.vue'
import CuratedGroup from '@/views/CuratedGroup.vue';
import DropInAdvisorHome from '@/views/DropInAdvisorHome.vue';
import DropInDesk from '@/views/DropInDesk.vue';
import Home from '@/views/Home.vue';
import Login from '@/layouts/Login.vue';
import NotFound from '@/views/NotFound.vue';
import PassengerManifest from '@/views/PassengerManifest.vue';
import Router from 'vue-router';
import Search from '@/views/Search.vue';
import StandardLayout from '@/layouts/StandardLayout.vue';
import store from '@/store';
import Student from '@/views/Student.vue';
import Vue from 'vue';

Vue.use(Router);

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
        store.dispatch('user/loadUser').then(user => {
          if (user.isAuthenticated) {
            if (_.trim(to.query.redirect)) {
              next(to.query.redirect);
            } else if (auth.isAdvisor(user) || user.isAdmin) {
              next('/home');
            } else {
              const schedulerDepartments = auth.schedulerForDepartments(user);
              if (_.size(schedulerDepartments)) {
                // The multi-department scheduler is NOT a use case we support, yet. Therefore,
                // we grab first deptCode from his/her profile.
                const deptCode = schedulerDepartments[0].code.toLowerCase();
                next({ path: `/appt/desk/${deptCode}` });
              } else {
                const dropInForDepartments = auth.dropInAdvisorForDepartments(user);
                if (_.size(dropInForDepartments)) {
                  const deptCode = dropInForDepartments[0].code.toLowerCase();
                  next({ path: `/home/${deptCode}` });
                } else {
                  next({ path: '/404' });
                }
              }
            }
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
      component: AppointmentDropIn,
      beforeEnter: auth.requiresScheduler,
      children: [
        {
          path: '/appt/desk/:deptCode',
          component: DropInDesk,
          meta: {
            title: 'Drop-in Appointments Desk'
          }
        },
        {
          path: '/scheduler/settings',
          component: Admin,
          meta: {
            title: 'Admin'
          }
        },
        {
          path: '/scheduler/404',
          component: NotFound,
          meta: {
            title: 'Not Found'
          }
        }
      ]
    },
    {
      path: '/',
      component: StandardLayout,
      beforeEnter: auth.requiresAdvisor,
      children: [
        {
          path: '/admin',
          name: 'admin',
          component: Admin,
          meta: {
            title: 'Flight Deck'
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
          path: '/curated/:id',
          component: CuratedGroup,
          props: true,
          meta: {
            title: 'Curated Group'
          }
        },
        {
          path: '/curate',
          component: CreateCuratedGroup,
          props: true,
          meta: {
            title: 'Create Curated Group'
          }
        },
        {
          path: '/groups/all',
          component: AllGroups,
          meta: {
            title: 'All Groups'
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
          path: '/student/:uid',
          component: Student,
          meta: {
            title: 'Student'
          }
        }
      ]
    },
    {
      path: '/',
      component: StandardLayout,
      beforeEnter: auth.requiresAdmin,
      children: [
        {
          path: '/admin/passengers',
          component: PassengerManifest,
          meta: {
            title: 'Passenger Manifest'
          }
        }
      ]
    },
    {
      path: '/',
      component: StandardLayout,
      beforeEnter: auth.requiresDropInAdvisor,
      children: [
        {
          path: '/home/:deptCode',
          component: DropInAdvisorHome,
          meta: {
            title: 'Home'
          }
        }
      ]
    },
    {
      path: '/',
      component: StandardLayout,
      beforeEnter: auth.requiresAuthenticated,
      children: [
        {
          beforeEnter: (to: any, from: any, next: any) => {
            store.dispatch('user/loadUser').then(user => {
              const schedulerDepartments = auth.schedulerForDepartments(user);
              if (_.size(schedulerDepartments) && !auth.isAdvisor(user) && !user.isAdmin) {
                const deptCode = schedulerDepartments[0].code.toLowerCase();
                next({ path: `/appt/desk/${deptCode}` });
              } else {
                const dropInForDepartments = auth.dropInAdvisorForDepartments(user);
                if (_.size(dropInForDepartments)) {
                  const deptCode = dropInForDepartments[0].code.toLowerCase();
                  next({ path: `/home/${deptCode}` });
                } else {
                  next();
                }
              }
            });
          },
          path: '/home',
          name: 'home',
          component: Home,
          meta: {
            title: 'Home'
          }
        },
        {
          beforeEnter: (to: any, from: any, next: any) => {
            store.dispatch('user/loadUser').then(user => {
              if (_.size(auth.schedulerForDepartments(user)) && !auth.isAdvisor(user) && !user.isAdmin) {
                next({ path: '/scheduler/404' });
              } else {
                next();
              }
            });
          },
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
  store.dispatch('context/clearAlertsInStore').then(() => next());
});

router.afterEach((to: any) => {
  let name = _.get(to, 'meta.title') || _.capitalize(to.name) || 'Welcome';
  document.title = `${name} | BOA`;
  if (to.query.error) {
    store.dispatch('context/reportError', {
      message: to.query.error
    });
  }
});

export default router;
