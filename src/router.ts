const AdmitStudent = () => import('@/views/AdmitStudent.vue')
const AdmitStudents = () => import('@/views/AdmitStudents.vue')
const AllCohorts = () => import('@/views/AllCohorts.vue')
const AllGroups = () => import('@/views/AllGroups.vue')
const AppointmentDropIn = () => import('@/layouts/AppointmentDropIn.vue')
const BatchDegreeCheck = () => import('@/views/degree/BatchDegreeCheck.vue')
const Cohort = () => import('@/views/Cohort.vue')
const Course = () => import('@/views/Course.vue')
const CreateCuratedGroup = () => import('@/views/CreateCuratedGroup.vue')
const CreateDegreeTemplate = () => import('@/views/degree/CreateDegreeTemplate.vue')
const CuratedGroup = () => import('@/views/CuratedGroup.vue')
const DegreeTemplate = () => import('@/views/degree/DegreeTemplate.vue')
const DropInAdvisorHome = () => import('@/views/DropInAdvisorHome.vue')
const DropInDesk = () => import('@/views/DropInDesk.vue')
const Error = () => import('@/views/Error.vue')
const FlightDataRecorder = () => import('@/views/FlightDataRecorder.vue')
const FlightDeck = () => import('@/views/FlightDeck.vue')
const Home = () => import('@/views/Home.vue')
const Login = () => import('@/layouts/Login.vue')
const ManageDegreeChecks = () => import('@/views/degree/ManageDegreeChecks.vue')
const NotFound = () => import('@/views/NotFound.vue')
const PassengerManifest = () => import('@/views/PassengerManifest.vue')
const PrintableDegreeTemplate = () => import('@/views/degree/PrintableDegreeTemplate.vue')
const Profile = () => import('@/views/Profile.vue')
const Search = () => import('@/views/Search.vue')
const StandardLayout = () => import('@/layouts/StandardLayout.vue')
const Student = () => import('@/views/Student.vue')
const StudentDegreeCheck = () => import('@/views/degree/StudentDegreeCheck.vue')
const StudentDegreeCreate = () => import('@/views/degree/StudentDegreeCreate.vue')
const StudentDegreeHistory = () => import('@/views/degree/StudentDegreeHistory.vue')
import _ from 'lodash'
import auth from './auth'
import Router from 'vue-router'
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
          name: 'Drop-in Appointments Desk'
        },
        {
          path: '/scheduler/profile',
          component: Profile,
          name: 'Scheduler Profile'
        },
        {
          path: '/scheduler/404',
          component: NotFound,
          name: 'Page Not Found'
        }
      ]
    },
    {
      path: '/',
      component: StandardLayout,
      beforeEnter: auth.requiresAdvisor,
      children: [
        {
          path: '/cohorts/all',
          component: AllCohorts,
          name: 'All Cohorts'
        },
        {
          path: '/cohort/:id',
          component: Cohort,
          name: 'Cohort'
        },
        {
          path: '/course/:termId/:sectionId',
          component: Course,
          name: 'Course'
        },
        {
          path: '/curated/:id',
          component: CuratedGroup,
          props: true,
          name: 'Curated Group'
        },
        {
          path: '/curate',
          component: CreateCuratedGroup,
          props: true,
          name: 'Create Curated Group'
        },
        {
          path: '/groups/all',
          component: AllGroups,
          name: 'All Groups'
        },
        {
          path: '/search',
          component: Search,
          name: 'Search'
        },
        {
          path: '/student/:uid',
          component: Student,
          name: 'Student'
        }
      ]
    },
    {
      path: '/',
      component: StandardLayout,
      beforeEnter: auth.requiresAdmin,
      children: [
        {
          path: '/admin',
          component: FlightDeck,
          name: 'Flight Deck'
        },
        {
          path: '/admin/passengers',
          component: PassengerManifest,
          name: 'Passenger Manifest'
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
          name: 'Drop-In Advisor Home'
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
          component: FlightDataRecorder,
          name: 'Flight Data Recorder'
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
          name: 'Admitted Student'
        },
        {
          path: '/admit/students',
          component: AdmitStudents,
          name: 'All Admitted Students'
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
          name: 'Manage Degree Checks'
        },
        {
          path: '/degree/batch',
          component: BatchDegreeCheck,
          name: 'Create Batch Degree Check'
        },
        {
          path: '/degree/new',
          component: CreateDegreeTemplate,
          name: 'Create New Degree Template',
        },
        {
          path: '/degree/:id',
          component: DegreeTemplate,
          name: 'Degree Template',
        },
        {
          path: '/student/:uid/degree/create',
          component: StudentDegreeCreate,
          name: 'Create Degree Check'
        },
        {
          path: '/student/:uid/degree/history',
          component: StudentDegreeHistory,
          name: 'Student Degree History',
        },
        {
          path: '/student/degree/:id',
          component: StudentDegreeCheck,
          name: 'Student Degree Check',
        }
      ]
    },
    {
      path: '/',
      beforeEnter: auth.requiresDegreeProgressPerm,
      component: PrintableDegreeTemplate,
      children: [
        {
          path: '/degree/:id/print',
          meta: {
            printable: true,
          },
          name: 'Print Degree Template'
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
          component: Home,
          name: 'Home'
        },
        {
          path: '/profile',
          component: Profile,
          name: 'Advisor Profile'
        },
        {
          path: '/error',
          component: Error,
          name: 'Error'
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
          name: 'Page not found'
        },
        {
          path: '*',
          redirect: '/404',
          name: 'Page not found'
        }
      ]
    }
  ]
})

router.afterEach((to: any) => {
  const pageTitle = _.get(to, 'name')
  document.title = `${pageTitle || _.capitalize(to.name) || 'Welcome'} | BOA`
  Vue.prototype.$announcer.assertive(`${pageTitle || 'Page'} is loading`)
})

export default router
