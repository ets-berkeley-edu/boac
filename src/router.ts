const AdmitStudent = () => import('@/views/AdmitStudent.vue')
const AdmitStudents = () => import('@/views/AdmitStudents.vue')
const AllCohorts = () => import('@/views/AllCohorts.vue')
const BatchDegreeCheck = () => import('@/views/degree/BatchDegreeCheck.vue')
const Cohort = () => import('@/views/Cohort.vue')
const CohortHistory = () => import('@/views/CohortHistory.vue')
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
const Login = () => import('./layouts/Login.vue')
const ManageDegreeChecks = () => import('@/views/degree/ManageDegreeChecks.vue')
const NotFound = () => import('@/views/NotFound.vue')
const PassengerManifest = () => import('@/views/PassengerManifest.vue')
const PeerAdvisor = () => import('@/layouts/PeerAdvisor.vue')
const PeerAdvisorManager = () => import('@/views/PeerAdvisorManager.vue')
const PrintableDegreeTemplate = () => import('@/views/degree/PrintableDegreeTemplate.vue')
const Profile = () => import('@/views/Profile.vue')
const SearchResults = () => import('@/views/SearchResults.vue')
const StandardLayout = () => import('@/layouts/StandardLayout.vue')
const Student = () => import('@/views/Student.vue')
const StudentDegreeCheck = () => import('@/views/degree/StudentDegreeCheck.vue')
const StudentDegreeCreate = () => import('@/views/degree/StudentDegreeCreate.vue')
const StudentDegreeHistory = () => import('@/views/degree/StudentDegreeHistory.vue')
import type {NavigationGuardNext, RouteLocation, RouteRecordRaw} from 'vue-router'
import {createRouter, createWebHistory} from 'vue-router'
import {filter, get, includes, size, toString, trim} from 'lodash'
import type {BoaUser} from './lib/types'
import PeerAdvisorHome from '@/views/PeerAdvisorHome.vue'
import {isAdvisor, isDirector, isPeerAdvisor, isPeerAdvisorManager} from '@/lib/boa-user'
import {useContextStore} from '@/stores/context'
import {useSearchStore} from '@/stores/search'


const $_goToLogin = (to: RouteLocation, next: NavigationGuardNext) => {
  next({
    path: '/',
    query: {
      error: to.query.error,
      redirect: to.name === 'Home' ? undefined : to.fullPath
    }
  })
}

const $_isCE3 = user => !!size(filter(user.departments, d => d.deptCode === 'ZCEEE' && includes(['advisor', 'director'], d.role)))

const $_requiresDegreeProgress = (to: RouteLocation, from: RouteLocation, next: NavigationGuardNext) => {
  const currentUser: BoaUser = useContextStore().currentUser
  if (currentUser.canReadDegreeProgress) {
    next()
  } else if (currentUser.isAuthenticated) {
    next({path: '/404'})
  } else {
    $_goToLogin(to, next)
  }
}

const routes:RouteRecordRaw[] = [
  {
    path: '/',
    component: Login,
    beforeEnter: (to: RouteLocation, from: RouteLocation, next: NavigationGuardNext) => {
      const currentUser: BoaUser = useContextStore().currentUser
      if (currentUser.isAuthenticated) {
        next(trim(toString(to.query.redirect)) || '/home')
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
    beforeEnter: (to: RouteLocation, from: RouteLocation, next: NavigationGuardNext) => {
      // Requires Advisor
      const currentUser: BoaUser = useContextStore().currentUser
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
        path: '/all/:mode',
        component: AllCohorts,
      },
      {
        path: '/cohort/history',
        component: CohortHistory,
        name: 'Cohort History'
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
        name: 'Curated Group'
      },
      {
        path: '/curate',
        component: CreateCuratedGroup,
        name: 'Create Curated Group'
      },
      {
        path: '/note/drafts',
        component: DraftNotes,
        name: 'Draft Notes'
      },
      {
        path: '/search',
        component: SearchResults,
        name: 'Search Results'
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
    beforeEnter: (to: RouteLocation, from: RouteLocation, next: NavigationGuardNext) => {
      // Requires Peer Advising Manager
      const currentUser: BoaUser = useContextStore().currentUser
      if (currentUser.isAuthenticated) {
        if (isPeerAdvisorManager(currentUser) || currentUser.isAdmin) {
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
        component: PeerAdvisorManager,
        name: 'Manage Peer Advisors',
        path: '/peer/management/:id'
      }
    ]
  },
  {
    path: '/',
    component: PeerAdvisor,
    beforeEnter: (to: RouteLocation, from: RouteLocation, next: NavigationGuardNext) => {
      // Requires Peer Advisor
      const currentUser: BoaUser = useContextStore().currentUser
      if (currentUser.isAuthenticated) {
        if (currentUser.isAdmin || isPeerAdvisor(currentUser)) {
          next()
        } else {
          next({path: '/peer_advisor/404'})
        }
      } else {
        $_goToLogin(to, next)
      }
    },
    children: [
      {
        path: '/peer_advisor/home',
        component: PeerAdvisorHome,
        name: 'Peer Advising'
      },
      {
        path: '/peer_advisor/profile',
        component: Profile,
        name: 'Advisor Profile'
      },
      {
        path: '/peer_advisor/error',
        component: Error,
        name: 'Error'
      },
      {
        path: '/peer_advisor/404',
        component: NotFound,
        name: 'Uh oh, page not found.'
      },
      {
        path: '/peer_advisor/:pathMatch(.*)*',
        redirect: '/peer_advisor/404',
        name: 'Page not found'
      }
    ]
  },
  {
    path: '/',
    component: StandardLayout,
    beforeEnter: (to: RouteLocation, from: RouteLocation, next: NavigationGuardNext) => {
      // Requires Admin
      const currentUser: BoaUser = useContextStore().currentUser
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
    beforeEnter: (to: RouteLocation, from: RouteLocation, next: NavigationGuardNext) => {
      // Requires Director
      const currentUser: BoaUser = useContextStore().currentUser
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
    beforeEnter: (to: RouteLocation, from: RouteLocation, next: NavigationGuardNext) => {
      // Requires CE3
      const currentUser: BoaUser = useContextStore().currentUser
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
    beforeEnter: $_requiresDegreeProgress,
    component: PrintableDegreeTemplate,
    meta: {
      printable: true,
    },
    name: 'Print Degree Template',
    path: '/degree/:id/print'
  },
  {
    path: '/',
    component: StandardLayout,
    beforeEnter: (to: RouteLocation, from: RouteLocation, next: NavigationGuardNext) => {
      const currentUser = useContextStore().currentUser
      if (currentUser.isAuthenticated) {
        if (isPeerAdvisor(currentUser)) {
          const path = `/peer_advisor${to.fullPath}`
          next({path: path})
        } else {
          next()
        }
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
        path: '/:pathMatch(.*)*',
        redirect: '/404',
        name: 'Page not found'
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to: RouteLocation) => {
  if (to.path !== '/search') {
    useSearchStore().resetAdvancedSearch()
  }
})

router.afterEach((to: RouteLocation, from: RouteLocation) => {
  const samePageLink = to.name === from.name && to.hash
  if (!samePageLink) {
    useContextStore().resetApplicationState()
    const pageTitle = get(to, 'name')
    document.title = `${pageTitle ? toString(pageTitle) : 'Welcome'} | BOA`
  }
})

export default router
