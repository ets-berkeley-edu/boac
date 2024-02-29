import axios from '@/plugins/axios'
import type {App} from 'vue'
import CKEditor from '@ckeditor/ckeditor5-vue'
import {createPinia} from 'pinia'
import {FocusTrap} from 'focus-trap-vue'
import {setupCalendar} from 'v-calendar'
import vuetify from './vuetify'
import defaultExport from 'vue3-shortkey'

export function registerPlugins (app: App) {
  app.use(axios, {baseUrl: import.meta.env.VITE_APP_API_BASE_URL})
    .use(CKEditor)
    .use(createPinia())
    .component('FocusTrap', FocusTrap)
    .use(setupCalendar, {})
    .use(vuetify)
    .use(defaultExport)
}
