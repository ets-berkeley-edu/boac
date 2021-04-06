import _ from 'lodash'
import auth from '@/auth'
import Vue from 'vue'
import VueAnalytics from 'vue-analytics'
import router from '@/router'
import store from '@/store'
import {event} from 'vue-analytics'

export default {
  async initializeCurrentUser() {
    if (Vue.prototype.$currentUser.isAuthenticated) {
      if (auth.isAdvisor(Vue.prototype.$currentUser) || auth.isDirector(Vue.prototype.$currentUser) || Vue.prototype.$currentUser.isAdmin) {
        const includeAdmits = Vue.prototype.$config.featureFlagAdmittedStudents && (
          Vue.prototype.$currentUser.isAdmin || auth.isCE3(Vue.prototype.$currentUser)
        )
        store.commit('currentUserExtras/setIncludeAdmits', includeAdmits)
        store.dispatch('currentUserExtras/loadMyCohorts').then(_.noop)
        store.dispatch('currentUserExtras/loadMyCuratedGroups').then(_.noop)
      }
    }
  },
  async mountGoogleAnalytics() {
    const options = {
      id: Vue.prototype.$config.googleAnalyticsId,
      checkDuplicatedScript: true,
      debug: {
        // If debug.enabled is true then browser console gets GA debug info.
        enabled: false
      },
      fields: {},
      router
    }
    Vue.use(VueAnalytics, options)

    if (Vue.prototype.$currentUser.uid) {
      options.fields['userId'] = Vue.prototype.$currentUser.uid
      const dept_code = Vue.prototype.$currentUser.isAdmin ? 'ADMIN' : _.keys(Vue.prototype.$currentUser.departments)[0]
      if (dept_code) {
        Vue.prototype.$ga.set('dimension1', dept_code)
      }
    }
    // BOA shortcuts
    Vue.prototype.$ga.appointmentEvent = (id, label, action) => event('Appointment', action, label, id)
    Vue.prototype.$ga.cohortEvent = (id, label, action) => event('Cohort', action, label, id)
    Vue.prototype.$ga.courseEvent = (id, label, action) => event('Course', action, label, id)
    Vue.prototype.$ga.curatedEvent = (id, label, action) => event('Curated Group', action, label, id)
    Vue.prototype.$ga.noteEvent = (id, label, action) => event('Advising Note', action, label, id)
    Vue.prototype.$ga.noteTemplateEvent = (id, label, action) => event('Advising Note Template', action, label, id)
    Vue.prototype.$ga.searchEvent = (label, action) => event('Search', action, label)
    Vue.prototype.$ga.studentAlert = action => event('Student Alert', action)
  }
}
