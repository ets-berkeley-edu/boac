import _ from 'lodash'
import App from './App.vue'
import axios from 'axios'
import BootstrapVue from 'bootstrap-vue'
import CKEditor from '@ckeditor/ckeditor5-vue'
import core from './core'
import Highcharts from 'highcharts'
import highchartsAccessibility from 'highcharts/modules/accessibility'
import HighchartsMore from 'highcharts/highcharts-more'
import lodash from 'lodash'
import mitt from 'mitt'
import moment from 'moment-timezone'
import router from './router'
import store from './store'
import VCalendar from 'v-calendar'
import Vue from 'vue'
import VueAnnouncer from '@vue-a11y/announcer'
import VueHighcharts from 'vue-highcharts'
import VueHotkey from 'v-hotkey'
import VueLodash from 'vue-lodash'
import VueMoment from 'vue-moment'
import {routerHistory, writeHistory} from 'vue-router-back-button'
import {library} from '@fortawesome/fontawesome-svg-core'
import {far} from '@fortawesome/free-regular-svg-icons'
import {fas} from '@fortawesome/free-solid-svg-icons'
import {faSpinner} from '@fortawesome/free-solid-svg-icons/faSpinner'
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome'

// Import Bootstrap an BootstrapVue CSS files (order is important)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

library.add(far, fas, faSpinner)
Vue.component('font-awesome', FontAwesomeIcon) // eslint-disable-line vue/component-definition-name-casing

// Allow cookies in Access-Control requests
axios.defaults.withCredentials = true

Vue.config.productionTip = false
Vue.use(BootstrapVue)
Vue.use(CKEditor)
Vue.use(VCalendar)
Vue.use(VueAnnouncer)
Vue.use(VueHotkey)
Vue.use(VueLodash, {lodash})
Vue.use(VueMoment, {moment})

HighchartsMore(Highcharts)
Vue.use(VueHighcharts, {Highcharts})
highchartsAccessibility(Highcharts)

Vue.directive('accessibleGrade', {
  bind: (el, binding) => el.innerHTML = binding.value && binding.value.replace('-', '&minus;').replace('+', '&plus;'),
  unbind: el => el.innerHTML = ''
})

// Emit and listen for events
Vue.prototype.$eventHub = mitt()

// Lodash
Vue.prototype.$_ = _

Vue.use(routerHistory)
router.afterEach(writeHistory)

const apiBaseUrl = process.env.VUE_APP_API_BASE_URL

const isHandledInComponent = error => {
  const errorUrl = _.get(error, 'response.config.url')
  return errorUrl && errorUrl.includes('/api/user/create_or_update')
}

const axiosErrorHandler = error => {
  const user = Vue.prototype.$currentUser
  const errorStatus = _.get(error, 'response.status')
  if (_.get(user, 'isAuthenticated')) {
    if (errorStatus === 404) {
      router.push({path: '/404'})
    } else if (!errorStatus || errorStatus >= 400) {
      const message = _.get(error, 'response.data.message') || error.message
      console.error(message)
      if (!isHandledInComponent(error)) {
        router.push({
          path: '/error',
          query: {
            m: message
          }
        })
      }
    }
  } else {
    router.push({
      path: '/login',
      query: {
        m: 'Your session has expired'
      }
    })
  }
}

axios.interceptors.response.use(
  response => response,
  error => {
    const errorStatus = _.get(error, 'response.status')
    if (_.includes([401, 403], errorStatus)) {
      // Refresh user in case his/her session expired.
      return axios.get(`${apiBaseUrl}/api/profile/my`).then(data => {
        Vue.prototype.$currentUser = data
        axiosErrorHandler(error)
        return Promise.reject(error)
      })
    } else {
      axiosErrorHandler(error)
      return Promise.reject(error)
    }
  }
)

axios.get(`${apiBaseUrl}/api/profile/my`).then(response => {
  Vue.prototype.$currentUser = response.data

  axios.get(`${apiBaseUrl}/api/config`).then(response => {
    Vue.prototype.$config = response.data
    Vue.prototype.$config.apiBaseUrl = apiBaseUrl
    Vue.prototype.$config.isVueAppDebugMode = _.trim(process.env.VUE_APP_DEBUG).toLowerCase() === 'true'
    store.commit('currentUserExtras/setUserPreference', {
      key: 'termId',
      value: `${Vue.prototype.$config.currentEnrollmentTermId}`
    })

    // Mount BOA
    new Vue({
      router,
      store,
      render: h => h(App)
    }).$mount('#app')

    if (Vue.prototype.$config.pingFrequency) {
      // Keep session alive with periodic requests
      setInterval(() => {
        axios.get(`${apiBaseUrl}/api/profile/my`).then(response => {
          if (!response.data.isAuthenticated) {
            Vue.prototype.$eventHub.emit('user-session-expired')
          }
        })
      }, Vue.prototype.$config.pingFrequency)
    }
    // The 'core' functions strictly manage state changes in $currentUser and other "prototype" objects.
    // For example, core functions might be invoked after a successful dev-auth login.
    Vue.prototype.$core = core
    Vue.prototype.$core.initializeCurrentUser().then(_.noop)
    Vue.prototype.$core.mountGoogleAnalytics().then(_.noop)
    // The following non-core function(s) do not involve "prototype" objects.
    store.dispatch('context/loadServiceAnnouncement').then(_.noop)
  })
})

Vue.prototype.$putFocusNextTick = (id: string, cssSelector?: string) => {
  Vue.prototype.$nextTick(() => {
    let counter = 0
    const putFocus = setInterval(() => {
      let el = document.getElementById(id)
      el = el && cssSelector ? el.querySelector(cssSelector) : el
      el && el.focus()
      if (el || ++counter > 5) {
        // Abort after success or three attempts
        clearInterval(putFocus)
      }
    }, 500)
  })
}
