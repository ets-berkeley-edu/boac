import 'v-calendar/style.css'
import App from './App.vue'
import axiosPlugin from '@/plugins/axios'
import axios from 'axios'
import CKEditor from '@ckeditor/ckeditor5-vue'
import Highcharts from 'highcharts'
import more from 'highcharts/highcharts-more'
import router from '@/router'
import VueHighcharts from 'vue-highcharts'
import vuetify from '@/plugins/vuetify'
import {DatePicker, setupCalendar} from 'v-calendar'
import {createApp} from 'vue'
import {createPinia} from 'pinia'
import {DateTime} from 'luxon'
import {FocusTrap} from 'focus-trap-vue'
import {get, trim} from 'lodash'
import {getServiceAnnouncement} from '@/api/config'
import {initializeAxios} from './main-utils'
import {useContextStore} from '@/stores/context'

const app = createApp(App)
  .use(axiosPlugin, {baseUrl: import.meta.env.VITE_APP_API_BASE_URL})
  .use(CKEditor)
  .use(createPinia())
  .use(setupCalendar, {})
  .use(VueHighcharts, {Highcharts})
  .use(vuetify)
  .component('focus-trap', FocusTrap)
  .component('DatePicker', DatePicker)
  .directive('accessibleGrade', {
    beforeMount(el, binding) {
      el.innerHTML = binding.value && binding.value.replace('-', '&minus;').replace('+', '&plus;')
    },
    unmounted(el) {
      el.innerHTML = ''
    }
  })

more(Highcharts)

initializeAxios(app, axios)

// Globals
app.config.globalProperties.$isInIframe = !!window.parent.frames.length
app.config.globalProperties.$DateTime = DateTime
app.config.globalProperties.$ready = (focusTarget?: string) => useContextStore().loadingComplete(focusTarget)

const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL

axios.get(`${apiBaseUrl}/api/profile/my`).then(response => {
  useContextStore().setCurrentUser(response.data)

  axios.get(`${apiBaseUrl}/api/config`).then(response => {
    useContextStore().setConfig({
      ...response.data,
      apiBaseUrl,
      isVueAppDebugMode: trim(import.meta.env.VITE_APP_DEBUG).toLowerCase() === 'true'
    })
    getServiceAnnouncement().then(data => useContextStore().setServiceAnnouncement(data))
    app.use(router).config.errorHandler = function (error, vm, info) {
      const message = get(error, 'message') || info
      const stacktrace = get(error, 'stack', null)
      console.log(`\n${message}\n${stacktrace}\n`)
      useContextStore().setApplicationState(500, message, stacktrace)
    }
    app.mount('#app')
  })
})
