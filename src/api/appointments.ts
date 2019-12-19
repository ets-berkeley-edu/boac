import axios from 'axios';
import store from '@/store';
import utils from '@/api/api-utils';
import Vue from "vue";

export function cancel(appointmentId, cancelReason, cancelReasonExplained) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/cancel`, {
      cancelReason,
      cancelReasonExplained
    })
    .then(response => {
      const uid = Vue.prototype.$currentUser.uid;
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} cancelled a drop-in appointment`, 'cancel');
      return response.data
    });
}

export function checkIn(
    advisorDeptCodes,
    advisorName,
    advisorRole,
    advisorUid,
    appointmentId
) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/check_in`, {
      advisorDeptCodes,
      advisorName,
      advisorRole,
      advisorUid
    }).then(response => {
      const uid = Vue.prototype.$currentUser.uid;
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} checked in a drop-in appointment`, 'check_in');
      return response.data
    });
}

export function create(
    deptCode,
    details,
    sid,
    appointmentType,
    topics,
    advisorDeptCodes?,
    advisorName?,
    advisorRole?,
    advisorUid?,
  ) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/create`, {
      advisorDeptCodes,
      advisorName,
      advisorRole,
      advisorUid,
      appointmentType,
      deptCode,
      details,
      sid,
      topics
    }).then(response => {
      const appointmentId = response.data.id;
      const uid = Vue.prototype.$currentUser.uid;
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} created an appointment`, 'create');
      return response.data
    }, () => null);
}

let $_findAdvisorsByNameCancel = axios.CancelToken.source();

export function findAdvisorsByName(query: string, limit: number) {
  if ($_findAdvisorsByNameCancel) {
     $_findAdvisorsByNameCancel.cancel();
  }
  $_findAdvisorsByNameCancel = axios.CancelToken.source();
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(
      `${apiBaseUrl}/api/appointments/advisors/find_by_name?q=${query}&limit=${limit}`,
      {cancelToken: $_findAdvisorsByNameCancel.token}
    ).then(response => response.data);
}

export function getAppointment(appointmentId) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}`)
    .then(response => response.data, () => null);
}

export function getDropInAppointmentWaitlist(deptCode) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/waitlist/${deptCode}`)
    .then(response => response.data, () => null);
}

export function markAppointmentRead(appointmentId) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/mark_read`)
    .then(response => {
      const uid = Vue.prototype.$currentUser.uid;
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} read an appointment`, 'read');
      return response.data
    }, () => null);
}

export function reopen(appointmentId) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/reopen`)
    .then(response => {
      const uid = Vue.prototype.$currentUser.uid;
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} reopened a drop-in appointment`, 'reopen');
      return response.data
    });
}

export function reserve(appointmentId, advisorUid) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/reserve`, {
      advisorUid,
    }).then(response => {
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${advisorUid} reserved a drop-in appointment`, 'reserve');
      return response.data
    });
}

export function unreserve(appointmentId) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/unreserve`)
    .then(response => {
      const uid = Vue.prototype.$currentUser.uid;
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} unreserve a drop-in appointment`, 'unreserve');
      return response.data
    });
}

export function update(appointmentId, details, topics) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/update`, {
      details,
      topics
    })
    .then(response => {
      const uid = Vue.prototype.$currentUser.uid;
      Vue.prototype.$ga.appointmentEvent(appointmentId, `Advisor ${uid} updated a drop-in appointment`, 'update');
      return response.data
    });
}
