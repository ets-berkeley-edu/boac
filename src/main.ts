import App from './App.vue'
import axios from 'axios'
import {DateTime} from 'luxon'
import router from '@/router'
import {createApp} from 'vue'
import {get, trim} from 'lodash'
import {initializeAxios} from './utils'
import {registerPlugins} from '@/plugins'
import {useContextStore} from '@/stores/context'

const app = createApp(App)

registerPlugins(app)
initializeAxios(app, axios)

// Globals
app.config.globalProperties.$isInIframe = !!window.parent.frames.length
app.config.globalProperties.$DateTime = DateTime
app.config.globalProperties.$ready = (focusTarget?: string) => useContextStore().loadingComplete(focusTarget)

const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL

axios.get(`${apiBaseUrl}/api/profile/my`).then(data => {
  useContextStore().setCurrentUser(data)

  axios.get(`${apiBaseUrl}/api/config`).then(data => {
    useContextStore().setConfig({
      ...data,
      apiBaseUrl,
      isVueAppDebugMode: trim(import.meta.env.VITE_APP_DEBUG).toLowerCase() === 'true'
    })
    app.use(router).config.errorHandler = function (error, vm, info) {
      const message = get(error, 'message') || info
      const stacktrace = get(error, 'stack', null)
      console.log(`\n${message}\n${stacktrace}\n`)
      useContextStore().setApplicationState(500, message, stacktrace)
    }
    app.mount('#app')
  })
})
