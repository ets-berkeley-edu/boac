import _ from 'lodash'
import router from './router'
import Vue from 'vue'
import VueGtag, {bootstrap} from 'vue-gtag'

export function initGoogleAnalytics() {
  return new Promise<void>(resolve => {
    const user = Vue.prototype.$currentUser
    if (user.isAuthenticated) {
      Vue.use(VueGtag, {
        appName: 'BOA',
        config: {
          checkDuplicatedScript: true,
          department: user.isAdmin ? 'ADMIN' : _.keys(user.departments)[0],
          fields: {},
          id: Vue.prototype.$config.googleAnalyticsId,
          params: {
            user_id: user.uid
          }
        },
        pageTrackerScreenviewEnabled: true
      }, router)
      bootstrap().then(() => {
        const track = (action, category, label?, id?) => {
          Vue.prototype.$gtag.event(action, {
            event_category: category,
            event_label: label,
            value: id
          })
        }
        // BOA shortcuts
        Vue.prototype.$ga = {
          appointment: action => track(action, 'Appointment'),
          cohort: (action, label?, id?) => track(action, 'Cohort', label, id),
          course: (action, label?) => track(action, 'Course', label),
          curated: (action, label?, id?) => track(action, 'Curated Group', label, id),
          degreeProgress: (action, label?) => track(action, 'Degree Progress', label),
          note: action => track(action, 'Advising Note'),
          noteTemplate: action => track(action, 'Note Template'),
          search: (action, label?) => track(action, 'Search', label),
          student: (action, label?) => track(action, 'Student', label)
        }
        resolve()
      })
    } else {
      resolve()
    }
  })
}
