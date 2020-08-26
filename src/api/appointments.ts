import axios from 'axios'
import utils from '@/api/api-utils'
import Vue from 'vue'

export function cancel(appointmentId, cancelReason, cancelReasonExplained) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/cancel`, {
      cancelReason,
      cancelReasonExplained
    })
    .then(response => {
      const uid = Vue.prototype.$currentUser.uid
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} cancelled a drop-in appointment`, 'cancel')
      return response.data
    })
}

export function checkIn(
    advisorUid,
    appointmentId
) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/check_in`, {
      advisorUid
    }).then(response => {
      const uid = Vue.prototype.$currentUser.uid
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} checked in a drop-in appointment`, 'check_in')
      return response.data
    })
}

export function create(
    deptCode,
    details,
    sid,
    appointmentType,
    topics,
    advisorUid?,
  ) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/create`, {
      advisorUid,
      appointmentType,
      deptCode,
      details,
      sid,
      topics
    }).then(response => {
      const appointmentId = response.data.id
      const uid = Vue.prototype.$currentUser.uid
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} created an appointment`, 'create')
      return response.data
    }, () => null)
}

export function getAppointment(appointmentId) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}`)
    .then(response => response.data, () => null)
}

export function getDropInAppointmentWaitlist(deptCode) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/waitlist/${deptCode}`)
    .then(response => response.data, () => null)
}

export function markAppointmentRead(appointmentId) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/mark_read`)
    .then(response => {
      const uid = Vue.prototype.$currentUser.uid
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} read an appointment`, 'read')
      return response.data
    }, () => null)
}

export function reopen(appointmentId) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/reopen`)
    .then(response => {
      const uid = Vue.prototype.$currentUser.uid
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} reopened a drop-in appointment`, 'reopen')
      return response.data
    })
}

export function reserve(appointmentId, advisorUid) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/reserve`, {
      advisorUid,
    }).then(response => {
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${advisorUid} reserved a drop-in appointment`, 'reserve')
      return response.data
    })
}

export function unreserve(appointmentId) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/unreserve`)
    .then(response => {
      const uid = Vue.prototype.$currentUser.uid
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} unreserve a drop-in appointment`, 'unreserve')
      return response.data
    })
}

export function update(appointmentId, details, topics) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/update`, {
      details,
      topics
    })
    .then(response => {
      const uid = Vue.prototype.$currentUser.uid
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} updated a drop-in appointment`, 'update')
      return response.data
    })
}
