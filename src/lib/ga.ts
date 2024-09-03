import {BoaConfig, CurrentUser, useContextStore} from '@/stores/context'
import {event} from 'vue-gtag'
import {map} from 'lodash'

export function getGtagConfig() {
  // GA4 config reference: https://developers.google.com/analytics/devguides/collection/ga4/reference/config
  const contextStore = useContextStore()
  const config: BoaConfig = contextStore.config
  const gaMeasurementId = config.gaMeasurementId
  const currentUser: CurrentUser = contextStore.currentUser
  const uid = currentUser.uid
  return {
    config: {id: gaMeasurementId},
    debug_mode: config.isVueAppDebugMode,
    disableScriptLoad: !gaMeasurementId,
    enabled: !!gaMeasurementId,
    params: {
      user_id: uid,
      user_properties: {
        dept_code: map(currentUser.departments || [], 'code'),
        title: currentUser.title,
        uid
      }
    }
  }
}

const track = (action: string, category: string, label?: string, id?: number | string) => {
  const currentUser: CurrentUser = useContextStore().currentUser
  if (currentUser.uid && !currentUser.isAdmin) {
    event(action, {event_category: category, event_label: label, value: id})
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
