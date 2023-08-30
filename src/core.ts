import _ from 'lodash'
import Vue from 'vue'

export function initGoogleAnalytics() {
  return new Promise<void>(resolve => {
    const googleAnalyticsId = process.env.VUE_APP_GOOGLE_ANALYTICS_ID
    const user = Vue.prototype.$currentUser
    if (googleAnalyticsId) {
      window.gtag('config', googleAnalyticsId, {
        user_id: user.uid,
        user_properties: {
          dept_code: _.map(user.departments || [], 'code'),
          title: user.title
        }
      })
    }
    const track = (action, category, label?, id?) => {
      // Report this event to Google Analytics if and only if certain conditions are true.
      if (googleAnalyticsId && user.uid && !user.isAdmin) {
        window.gtag('event', action, {
          event_category: category,
          event_label: label,
          value: id
        })
      }
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
}
