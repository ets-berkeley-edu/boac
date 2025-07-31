import {configure, event} from 'vue-gtag'
import {map} from 'lodash'
import type {BoaUser} from '@/lib/types'
import {useContextStore} from '@/stores/context'

export function initGoogleAnalytics() {
  // GA4 config reference: https://developers.google.com/analytics/devguides/collection/ga4/reference/config
  const contextStore = useContextStore()
  if (isGoogleAnalyticsEnabled()) {
    const currentUser: BoaUser = contextStore.currentUser
    configure({
      tagId: contextStore.config.gaMeasurementId,
      config: {
        user_id: currentUser.uid,
        user_properties: {
          dept_code: map(currentUser.departments || [], 'deptCode'),
          title: currentUser.title,
          uid: currentUser.uid
        }
      }
    })
  }
}

const isGoogleAnalyticsEnabled = () => {
  const contextStore = useContextStore()
  const gaMeasurementId = contextStore.config.gaMeasurementId
  const currentUser: BoaUser = contextStore.currentUser
  return currentUser.uid && !currentUser.isAdmin && gaMeasurementId
}

const track = (action: string, category: string, label?: string, id?: number | undefined) => {
  const currentUser: BoaUser = useContextStore().currentUser
  if (currentUser.uid && !currentUser.isAdmin) {
    event(action, {event_category: category, event_label: label, value: id})
  }
}

export default {
  appointment: (action: string) => track(action, 'Appointment'),
  cohort: (action: string, label?: string, id?: number | undefined) => track(action, 'Cohort', label, id),
  course: (action: string, label?: string) => track(action, 'Course', label),
  curated: (action: string, label?: string, id?: number | undefined) => track(action, 'Curated Group', label, id),
  degreeProgress: (action: string, label?: string) => track(action, 'Degree Progress', label),
  note: (action: string) => track(action, 'Advising Note'),
  noteTemplate: (action: string) => track(action, 'Note Template'),
  search: (action: string, label?: string) => track(action, 'Search', label),
  student: (action: string, label?: string) => track(action, 'Student', label)
}
