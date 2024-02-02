const AdmitStudent = () => import('@/views/AdmitStudent.vue')
const AdmitStudents = () => import('@/views/AdmitStudents.vue')
const AllCohorts = () => import('@/views/AllCohorts.vue')
const AllGroups = () => import('@/views/AllGroups.vue')
const BatchDegreeCheck = () => import('@/views/degree/BatchDegreeCheck.vue')
const Cohort = () => import('@/views/Cohort.vue')
const Course = () => import('@/views/Course.vue')
const CreateCuratedGroup = () => import('@/views/CreateCuratedGroup.vue')
const CreateDegreeTemplate = () => import('@/views/degree/CreateDegreeTemplate.vue')
const CuratedGroup = () => import('@/views/CuratedGroup.vue')
const DegreeTemplate = () => import('@/views/degree/DegreeTemplate.vue')
const DraftNotes = () => import('@/views/DraftNotes.vue')
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
const SearchResults = () => import('@/views/SearchResults.vue')
const StandardLayout = () => import('@/layouts/StandardLayout.vue')
const Student = () => import('@/views/Student.vue')
const StudentDegreeCheck = () => import('@/views/degree/StudentDegreeCheck.vue')
const StudentDegreeCreate = () => import('@/views/degree/StudentDegreeCreate.vue')
const StudentDegreeHistory = () => import('@/views/degree/StudentDegreeHistory.vue')
import _ from 'lodash'
import Router from 'vue-router'
import store from './store'
import Vue from 'vue'
import {isAdvisor, isDirector} from '@/berkeley'

Vue.use(Router)

const $_goToLogin = (to: any, next: any) => {
  next({
    path: '/login',
    query: {
      error: to.query.error,
      redirect: to.name === 'Home' ? undefined : to.fullPath
    }
  })
}

const $_isCE3 = user => !!_.size(_.filter(user.departments, d => d.code === 'ZCEEE' && _.includes(['advisor', 'director'], d.role)))

const $_requiresDegreeProgress = (to: any, from: any, next: any) => {
  const currentUser = store.getters['context/currentUser']
  if (currentUser.canReadDegreeProgress) {
    next()
  } else if (currentUser.isAuthenticated) {
    next({path: '/404'})
  } else {
    $_goToLogin(to, next)
  }
}

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
        const currentUser = store.getters['context/currentUser']
        if (currentUser.isAuthenticated) {
          if (_.trim(to.query.redirect)) {
            next(to.query.redirect)
          } else if (isAdvisor(currentUser) || isDirector(currentUser) || currentUser.isAdmin) {
            next('/home')
          } else {
            next({path: '/404'})
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
      component: StandardLayout,
      beforeEnter: (to: any, from: any, next: any) => {
        // Requires Advisor
        const currentUser = store.getters['context/currentUser']
        if (currentUser.isAuthenticated) {
          if (isAdvisor(currentUser) || isDirector(currentUser) || currentUser.isAdmin) {
            next()
          } else {
            next({path: '/404'})
          }
        } else {
          $_goToLogin(to, next)
        }
      },
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
          path: '/note/drafts',
          component: DraftNotes,
          props: true,
          name: 'Draft Notes'
        },
        {
          path: '/search',
          component: SearchResults,
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
      beforeEnter: (to: any, from: any, next: any) => {
        // Requires Admin
        const currentUser = store.getters['context/currentUser']
        if (currentUser.isAuthenticated) {
          if (currentUser.isAdmin) {
            next()
          } else {
            next({path: '/404'})
          }
        } else {
          $_goToLogin(to, next)
        }
      },
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
      beforeEnter: (to: any, from: any, next: any) => {
        // Requires Director
        const currentUser = store.getters['context/currentUser']
        if (currentUser.isAuthenticated) {
          if (isDirector(currentUser) || currentUser.isAdmin) {
            next()
          } else {
            next({path: '/404'})
          }
        } else {
          $_goToLogin(to, next)
        }
      },
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
      beforeEnter: (to: any, from: any, next: any) => {
        // Requires CE3
        const currentUser = store.getters['context/currentUser']
        if (currentUser.isAuthenticated) {
          if (currentUser.isAdmin || $_isCE3(currentUser)) {
            next()
          } else {
            next({path: '/404'})
          }
        } else {
          $_goToLogin(to, next)
        }
      },
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
      beforeEnter: $_requiresDegreeProgress,
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
      beforeEnter: $_requiresDegreeProgress,
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
      beforeEnter: (to: any, from: any, next: any) => {
        // Requires Authenticated
        if (store.getters['context/currentUser'].isAuthenticated) {
          next()
        } else {
          $_goToLogin(to, next)
        }
      },
      children: [
        {
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
          path: '/404',
          component: NotFound,
          name: '404'
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

router.afterEach((to: any, from: any) => {
  // TODO
  const sameRoute = to.name === from.name && to.hash
  if (!sameRoute) {
    store.commit('context/loadingStart', to)
    const pageTitle = _.get(to, 'name')
    document.title = `${_.capitalize(pageTitle) || 'Welcome'} | BOA`
  }
})

export default router
