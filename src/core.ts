import _ from 'lodash'
import Vue from 'vue'
import router from '@/router'
import VueGtag, {bootstrap} from 'vue-gtag'

export default {
  async initializeCurrentUser() {
    const user = Vue.prototype.$currentUser
    if (user.isAuthenticated) {
      bootstrap().then(() => {
        Vue.prototype.$gtag.config({
          dimension1: user.isAdmin ? 'ADMIN' : _.keys(user.departments)[0],
          router,
          user_id: user.uid
        })
      })
    }
  },
  async mountGoogleAnalytics() {
    Vue.use(VueGtag, {
      bootstrap: false,
      config: {
        checkDuplicatedScript: true,
        debug: {
          // If debug.enabled is true then browser console gets GA debug info.
          enabled: false
        },
        fields: {},
        id: Vue.prototype.$config.googleAnalyticsId,
        pageTrackerScreenviewEnabled: true
      }
    })
    const track = (action, category, label?, value?) => {
      Vue.prototype.$gtag.event(action, {
        event_category: category,
        event_label: label,
        value
      })
    }
    // BOA shortcuts
    Vue.prototype.$ga = {
      appointmentEvent: (id, label, action) => track('Appointment', action, label, id),
      cohortEvent: (id, label, action) => track('Cohort', action, label, id),
      courseEvent: (id, label, action) => track('Course', action, label, id),
      curatedEvent: (id, label, action) => track('Curated Group', action, label, id),
      noteEvent: (id, label, action) => track('Advising Note', action, label, id),
      noteTemplateEvent: (id, label, action) => track('Advising Note Template', action, label, id),
      searchEvent: (label, action) => track('Search', action, label),
      studentAlert: action => track('Student Alert', action)
    }
  }
}
