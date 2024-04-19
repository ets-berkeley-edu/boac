import 'v-calendar/style.css'
import axios from '@/plugins/axios'
import CKEditor from '@ckeditor/ckeditor5-vue'
import Highcharts from 'highcharts'
import more from 'highcharts/highcharts-more'
import VueHighcharts from 'vue-highcharts'
import vuetify from './vuetify'
import type {App} from 'vue'
import {Calendar, DatePicker, setupCalendar} from 'v-calendar'
import {createPinia} from 'pinia'
import {FocusTrap} from 'focus-trap-vue'

export function registerPlugins (app: App) {
  app.use(axios, {baseUrl: import.meta.env.VITE_APP_API_BASE_URL})
    .use(CKEditor)
    .use(createPinia())
    .use(setupCalendar, {})
    .use(VueHighcharts, {Highcharts})
    .use(vuetify)
    .component('focus-trap', FocusTrap)
    .component('elegant-calendar', Calendar)
    .component('elegant-date-picker', DatePicker)
    .directive('accessibleGrade', {
      beforeMount(el, binding) {
        el.innerHTML = binding.value && binding.value.replace('-', '&minus;').replace('+', '&plus;')
      },
      unmounted(el) {
        el.innerHTML = ''
      }
    })
  more(Highcharts)
}
