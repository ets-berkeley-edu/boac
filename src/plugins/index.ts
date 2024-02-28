import Autocomplete from '@trevoreyre/autocomplete-vue'
import axios from '@/plugins/axios'
import type {App} from 'vue'
import vuetify from './vuetify'
import {createPinia} from 'pinia'
import '@trevoreyre/autocomplete-vue/dist/style.css'

export function registerPlugins (app: App) {
  app
    .use(Autocomplete)
    .use(axios, {baseUrl: import.meta.env.VITE_APP_API_BASE_URL})
    .use(createPinia())
    .use(vuetify)
}
