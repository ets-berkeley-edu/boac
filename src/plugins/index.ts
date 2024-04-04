import 'v-calendar/style.css'
import axios from '@/plugins/axios'
import {Calendar, DatePicker, setupCalendar} from 'v-calendar'
import CKEditor from '@ckeditor/ckeditor5-vue'
import type {App} from 'vue'
import vuetify from './vuetify'
import {createPinia} from 'pinia'
import {FocusTrap} from 'focus-trap-vue'

export function registerPlugins (app: App) {
  app.use(axios, {baseUrl: import.meta.env.VITE_APP_API_BASE_URL})
    .use(CKEditor)
    .use(createPinia())
    .use(setupCalendar, {})
    .use(vuetify)
    .component('focus-trap', FocusTrap)
    .component('elegant-calendar', Calendar)
    .component('elegant-date-picker', DatePicker)
}
