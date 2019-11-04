import axios from 'axios';
import store from '@/store';
import utils from '@/api/api-utils';

export function cancel(appointmentId, cancelReason, cancelReasonExplained) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/cancel`, {
      cancelReason,
      cancelReasonExplained
    })
    .then(response => {
      store.dispatch('user/gaAppointmentEvent', {
        id: appointmentId,
        name: `Advisor ${store.getters['user/uid']} canceled a drop-in appointment`,
        action: 'cancel'
      });
      return response.data
    }, () => null);
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
      store.dispatch('user/gaAppointmentEvent', {
        id: appointmentId,
        name: `Advisor ${store.getters['user/uid']} checked in a drop-in appointment`,
        action: 'check_in'
      });
      return response.data
    }, () => null);
}

export function create(deptCode, details, sid, appointmentType, topics) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/create`, {
      appointmentType,
      deptCode,
      details,
      sid,
      topics
    }).then(response => {
      const appointmentId = response.data.id;
      store.dispatch('user/gaAppointmentEvent', {
        id: appointmentId,
        name: `Advisor ${store.getters['user/uid']} created an appointment`,
        action: 'create'
      });
      return response.data
    }, () => null);
}

export function findAdvisorsByName(query: string, limit: number) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/appointments/advisors/find_by_name?q=${query}&limit=${limit}`)
    .then(response => response.data);
}

export function getDropInAppointmentWaitlist(deptCode) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/waitlist/${deptCode}`)
    .then(response => response.data, () => null);
}

export function getAllTopics(includeDeleted: boolean) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/topics?includeDeleted=${includeDeleted}`)
    .then(response => response.data, () => null);
}

export function markAppointmentRead(appointmentId) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/mark_read`)
    .then(response => {
      store.dispatch('user/gaAppointmentEvent', {
        id: appointmentId,
        name: `Advisor ${store.getters['user/uid']} read an appointment`,
        action: 'read'
      });
      return response.data
    }, () => null);
}

export function reserve(appointmentId) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/reserve`)
    .then(response => {
      store.dispatch('user/gaAppointmentEvent', {
        id: appointmentId,
        name: `Advisor ${store.getters['user/uid']} reserved a drop-in appointment`,
        action: 'reserve'
      });
      return response.data
    }, () => null);
}

export function unreserve(appointmentId) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/unreserve`)
    .then(response => {
      store.dispatch('user/gaAppointmentEvent', {
        id: appointmentId,
        name: `Advisor ${store.getters['user/uid']} unreserve a drop-in appointment`,
        action: 'unreserve'
      });
      return response.data
    }, () => null);
}
