import accessibility from 'highcharts/modules/accessibility'
import App from './App.vue'
import axiosPlugin from '@/plugins/axios'
import axios from 'axios'
import CKEditor from '@ckeditor/ckeditor5-vue'
import Highcharts from 'highcharts'
import more from 'highcharts/highcharts-more'
import router from '@/router'
import VueGtag from 'vue-gtag'
import VueHighcharts from 'vue-highcharts'
import vuetify from '@/plugins/vuetify'
import {createApp} from 'vue'
import {createPinia} from 'pinia'
import {trim} from 'lodash'
import {getServiceAnnouncement} from '@/api/config'
import {appErrorHandler, initializeAxios} from '@/main-utils'
import {setupCalendar} from 'v-calendar'
import {useContextStore} from '@/stores/context'
import linkifyHtml from 'linkify-html'
import {getGtagConfig} from '@/lib/ga'

const apiBaseUrl: string = import.meta.env.VITE_APP_API_BASE_URL
const isVueAppDebugMode: boolean = trim(import.meta.env.VITE_APP_DEBUG).toLowerCase() === 'true'

const app = createApp(App)
app.config.errorHandler = appErrorHandler
accessibility(Highcharts)
app.use(axiosPlugin, {baseUrl: apiBaseUrl})
  .use(CKEditor)
  .use(createPinia())
  .use(setupCalendar, {})
  .use(VueHighcharts, {Highcharts})
  .use(vuetify)
  .directive('accessibleGrade', {
    beforeMount: (el, binding) => el.innerHTML = binding.value && binding.value.replace('-', '&minus;').replace('+', '&plus;'),
    unmounted: el => el.innerHTML = ''
  })
  .directive('linkified', {
    // See https://github.com/Hypercontext/linkifyjs?tab=readme-ov-file#installation-and-usage
    beforeMount: el => el.innerHTML = linkifyHtml(el.innerHTML, {defaultProtocol: 'https'})
  })

more(Highcharts)
initializeAxios(axios)

axios.get(`${apiBaseUrl}/api/profile/my`).then(response => {
  const contextStore = useContextStore()
  contextStore.setCurrentUser(response.data)

  axios.get(`${apiBaseUrl}/api/config`).then(response => {
    contextStore.setConfig({...response.data, apiBaseUrl, isVueAppDebugMode})
    getServiceAnnouncement().then(data => contextStore.setServiceAnnouncement(data))
    app.use(router)
      .use(VueGtag, getGtagConfig())
      .mount('#app')
  })
})
