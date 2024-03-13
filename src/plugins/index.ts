import 'v-calendar/style.css'
import axios from '@/plugins/axios'
import BaseInput from 'v-calendar'
import CKEditor from '@ckeditor/ckeditor5-vue'
import defaultExport from 'vue3-shortkey'
import type {App} from 'vue'
import vuetify from './vuetify'
import {createPinia} from 'pinia'
import {FocusTrap} from 'focus-trap-vue'
import {Calendar, DatePicker, setupCalendar} from 'v-calendar'

export function registerPlugins (app: App) {
  app.use(axios, {baseUrl: import.meta.env.VITE_APP_API_BASE_URL})
    .use(CKEditor)
    .use(createPinia())
    .use(setupCalendar, {})
    .use(vuetify)
    .use(defaultExport)
    .component('FocusTrap', FocusTrap)
    .component('VBaseInput', BaseInput)
    .component('VCalendar', Calendar)
    .component('VDatePicker', DatePicker)
}
