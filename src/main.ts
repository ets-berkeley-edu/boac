import _ from 'lodash'
import App from './App.vue'
import axios from 'axios'
import BootstrapVue from 'bootstrap-vue'
import CKEditor from '@ckeditor/ckeditor5-vue2'
import Highcharts from 'highcharts'
import highchartsAccessibility from 'highcharts/modules/accessibility'
import HighchartsMore from 'highcharts/highcharts-more'
import linkify from 'vue-linkify'
import moment from 'moment'
import router from './router'
import store from './store'
import VCalendar from 'v-calendar'
import Vue from 'vue'
import VueAnnouncer from '@vue-a11y/announcer'
import VueHighcharts from 'vue-highcharts'
import VueHotkey from 'v-hotkey'
import {routerHistory, writeHistory} from 'vue-router-back-button'
import {library} from '@fortawesome/fontawesome-svg-core'
import {far} from '@fortawesome/free-regular-svg-icons'
import {fas} from '@fortawesome/free-solid-svg-icons'
import {faSpinner} from '@fortawesome/free-solid-svg-icons/faSpinner'
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome'
import {initGoogleAnalytics} from '@/core'

// Import Bootstrap an BootstrapVue CSS files (order is important)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

const isVueAppDebugMode = _.trim(process.env.VUE_APP_DEBUG).toLowerCase() === 'true'

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

HighchartsMore(Highcharts)
Vue.use(VueHighcharts, {Highcharts})
highchartsAccessibility(Highcharts)

Vue.directive('accessibleGrade', {
  bind: (el, binding) => el.innerHTML = binding.value && binding.value.replace('-', '&minus;').replace('+', '&plus;'),
  unbind: el => el.innerHTML = ''
})
Vue.directive('linkified', linkify)

// Global utilities
Vue.prototype.$_ = _
Vue.prototype.$moment = moment

Vue.use(routerHistory)
router.afterEach(writeHistory)

const apiBaseUrl = process.env.VUE_APP_API_BASE_URL

const axiosErrorHandler = error => {
  const user = Vue.prototype.$currentUser
  const errorStatus = _.get(error, 'response.status')
  if (!_.get(user, 'isAuthenticated')) {
    router.push({
      path: '/login',
      query: {
        m: 'Your session has expired'
      }
    })
  } else if (errorStatus === 404) {
    router.push({path: '/404'})
  } else if (!axios.isCancel(error)) {
    const skipRedirect = ['/api/user/create_or_update']
    const url = _.get(error, 'response.config.url')
    if (!_.find(skipRedirect, path => _.includes(url, path))) {
      router.push({
        path: '/error',
        query: {
          m: _.get(error, 'response.data.message') || error.message,
          s: errorStatus,
          t: _.get(error, 'response.statusText')
        }
      })
    }
  }
}

axios.interceptors.response.use(
  response => response,
  error => {
    const errorStatus = _.get(error, 'response.status')
    if (_.includes([401, 403], errorStatus)) {
      // Refresh user in case his/her session expired.
      return axios.get(`${apiBaseUrl}/api/profile/my`).then(response => {
        Vue.prototype.$currentUser = Vue.observable(response.data)
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
  Vue.prototype.$currentUser = Vue.observable(response.data)
  axios.get(`${apiBaseUrl}/api/config`).then(response => {
    Vue.prototype.$config = response.data
    Vue.prototype.$config.apiBaseUrl = apiBaseUrl
    const ebEnvironment = Vue.prototype.$config.ebEnvironment
    Vue.prototype.$config.isProduction = ebEnvironment && ebEnvironment.toLowerCase().includes('prod')
    Vue.prototype.$config.isVueAppDebugMode = isVueAppDebugMode

    initGoogleAnalytics().then(() => {
      store.dispatch('context/loadServiceAnnouncement')
      // Mount BOA
      new Vue({
        router,
        store,
        render: h => h(App)
      }).$mount('#app')

      if (Vue.prototype.$config.pingFrequency) {
        // Keep session alive with periodic requests
        setInterval(() => {
          axios.get(`${apiBaseUrl}/api/user/session_keep_alive`).then(response => {
            if (!response.data.isAuthenticated) {
              store.commit('context/broadcast', 'user-session-expired')
            }
          })
        }, Vue.prototype.$config.pingFrequency)
      }
    })
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
