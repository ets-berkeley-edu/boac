import axios from 'axios'
import utils from '@/api/api-utils'
import Vue from 'vue'

const $_track = action => Vue.prototype.$ga.appointment(action)

export function cancel(appointmentId, cancelReason, cancelReasonExplained) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/cancel`, {
      cancelReason,
      cancelReasonExplained
    })
    .then(response => response.data)
}

export function checkIn(
    advisorUid,
    appointmentId
) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/check_in`, {
      advisorUid
    }).then(response => response.data)
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
      $_track('create')
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
      $_track('read')
      return response.data
    }, () => null)
}

export function reopen(appointmentId) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/reopen`)
    .then(response => response.data)
}

export function reserve(appointmentId, advisorUid) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/reserve`, {
      advisorUid,
    }).then(response => response.data)
}

export function unreserve(appointmentId) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/unreserve`)
    .then(response => response.data)
}

export function update(appointmentId, details, topics) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/update`, {
      details,
      topics
    }).then(response => {
      $_track('update')
      return response.data
    })
}
