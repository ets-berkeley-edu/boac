import _ from 'lodash'
import AdmitStudent from '@/views/AdmitStudent.vue'
import AdmitStudents from '@/views/AdmitStudents.vue'
import AllCohorts from '@/views/AllCohorts.vue'
import AllGroups from '@/views/AllGroups.vue'
import Analytics from '@/views/Analytics.vue'
import AppointmentDropIn from '@/layouts/AppointmentDropIn.vue'
import auth from './auth'
import Cohort from '@/views/Cohort.vue'
import Course from '@/views/Course.vue'
import CreateCuratedGroup from '@/views/CreateCuratedGroup.vue'
import CreateDegreeTemplate from '@/views/degree/CreateDegreeTemplate.vue'
import CuratedGroup from '@/views/CuratedGroup.vue'
import ManageDegreeChecks from '@/views/degree/ManageDegreeChecks.vue'
import DegreeTemplate from '@/views/degree/DegreeTemplate.vue'
import DropInAdvisorHome from '@/views/DropInAdvisorHome.vue'
import DropInDesk from '@/views/DropInDesk.vue'
import Error from '@/views/Error.vue'
import FlightDeck from '@/views/FlightDeck.vue'
import Home from '@/views/Home.vue'
import Login from '@/layouts/Login.vue'
import NotFound from '@/views/NotFound.vue'
import PassengerManifest from '@/views/PassengerManifest.vue'
import Profile from '@/views/Profile.vue'
import Router from 'vue-router'
import Search from '@/views/Search.vue'
import StandardLayout from '@/layouts/StandardLayout.vue'
import Student from '@/views/Student.vue'
import StudentDegreeCheck from '@/views/degree/StudentDegreeCheck.vue'
import StudentDegreeCreate from '@/views/degree/StudentDegreeCreate.vue'
import StudentDegreeHistory from '@/views/degree/StudentDegreeHistory.vue'
import Vue from 'vue'

Vue.use(Router)

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
        const currentUser = Vue.prototype.$currentUser
        if (currentUser.isAuthenticated) {
          if (_.trim(to.query.redirect)) {
            next(to.query.redirect)
          } else if (auth.isAdvisor(currentUser) || auth.isDirector(currentUser) || currentUser.isAdmin) {
            next('/home')
          } else {
            const deptCodes = auth.getSchedulerDeptCodes(currentUser)
            if (_.size(deptCodes)) {
              // The multi-department scheduler is NOT a use case we support, yet. Therefore,
              // we grab first deptCode from his/her profile.
              const deptCode = deptCodes[0].toLowerCase()
              next({path: `/appt/desk/${deptCode}`})
            } else {
              next({path: '/404'})
            }
          }
        } else {
          next()
        }
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
          path: '/scheduler/profile',
          component: Profile,
          meta: {
            title: 'Scheduler Profile'
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
          component: FlightDeck,
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
      beforeEnter: auth.requiresDirector,
      children: [
        {
          path: '/analytics/:deptCode',
          component: Analytics,
          meta: {
            title: 'Flight Data Recorder'
          }
        }
      ]
    },
    {
      path: '/',
      component: StandardLayout,
      beforeEnter: auth.requiresCE3,
      children: [
        {
          path: '/admit/student/:sid',
          component: AdmitStudent,
          meta: {
            title: 'Admitted Student'
          }
        },
        {
          path: '/admit/students',
          component: AdmitStudents,
          meta: {
            title: 'Admitted Students'
          }
        }
      ]
    },
    {
      path: '/',
      component: StandardLayout,
      beforeEnter: auth.requiresDegreeProgressPerm,
      children: [
        {
          path: '/degrees',
          component: ManageDegreeChecks,
          meta: {
            title: 'Managing Degree Checks'
          }
        },
        {
          path: '/degree/new',
          component: CreateDegreeTemplate,
          meta: {
            title: 'Create New Degree',
          },
        },
        {
          path: '/degree/:id',
          component: DegreeTemplate,
          meta: {
            title: 'Degree',
          },
        },
        {
          path: '/student/:uid/degree/create',
          component: StudentDegreeCreate,
          meta: {
            title: 'Create Degree',
          },
        },
        {
          path: '/student/:uid/degree/history',
          component: StudentDegreeHistory,
          meta: {
            title: 'Student Degree History',
          },
        },
        {
          path: '/student/:uid/degree/:id',
          component: StudentDegreeCheck,
          meta: {
            title: 'Student Degree',
          },
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
            const currentUser = Vue.prototype.$currentUser
            const deptCodes = auth.getSchedulerDeptCodes(currentUser)
            if (_.size(deptCodes) && !(auth.isAdvisor(currentUser) || auth.isDirector(currentUser)) && !currentUser.isAdmin) {
              const deptCode = deptCodes[0].toLowerCase()
              next({path: `/appt/desk/${deptCode}`})
            } else {
              if (_.size(currentUser.dropInAdvisorStatus)) {
                // We assume drop-in advisor status for one department only.
                const deptCode = currentUser.dropInAdvisorStatus[0].deptCode.toLowerCase()
                next({path: `/home/${deptCode}`})
              } else {
                next()
              }
            }
          },
          path: '/home',
          name: 'home',
          component: Home,
          meta: {
            title: 'Home'
          }
        },
        {
          path: '/profile',
          name: 'profile',
          component: Profile,
          meta: {
            title: 'Profile'
          }
        },
        {
          path: '/error',
          component: Error,
          meta: {
            title: 'Error'
          }
        },
        {
          beforeEnter: (to: any, from: any, next: any) => {
            const currentUser = Vue.prototype.$currentUser
            if (_.size(auth.getSchedulerDeptCodes(currentUser)) && !(auth.isAdvisor(currentUser) || auth.isDirector(currentUser)) && !currentUser.isAdmin) {
              next({path: '/scheduler/404'})
            } else {
              next()
            }
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
})

router.afterEach((to: any) => {
  const pageTitle = _.get(to, 'meta.title')
  document.title = `${pageTitle || _.capitalize(to.name) || 'Welcome'} | BOA`
  Vue.prototype.$announcer.assertive(`${pageTitle || 'Page'} is loading`)
})

export default router
