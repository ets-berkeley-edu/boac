import axios from '@/plugins/axios'
import type {App} from 'vue'
import vuetify from './vuetify'
import {createPinia} from 'pinia'

export function registerPlugins (app: App) {
  app
    .use(axios, {baseUrl: import.meta.env.VITE_APP_API_BASE_URL})
    .use(createPinia())
    .use(vuetify)
}
