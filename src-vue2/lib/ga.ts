import _ from 'lodash'
import store from '@/store'

export function initGoogleAnalytics() {
  return new Promise<void>(resolve => {
    const googleAnalyticsId = process.env.VUE_APP_GOOGLE_ANALYTICS_ID
    if (googleAnalyticsId) {
      const user = store.getters['context/currentUser']
      const uid = user.uid
      window.gtag('config', googleAnalyticsId, {
        user_id: uid,
        user_properties: {
          dept_code: _.map(user.departments || [], 'code'),
          title: user.title,
          uid
        }
      })
    }
    resolve()
  })
}

const track = (action, category, label?, id?) => {
  const googleAnalyticsId = process.env.VUE_APP_GOOGLE_ANALYTICS_ID
  const user = store.getters['context/currentUser']
  const uid = user.uid
  if (googleAnalyticsId && uid && !user.isAdmin) {
    window.gtag('event', action, {
      event_category: category,
      event_label: label,
      value: id
    })
  }
}

export default {
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
