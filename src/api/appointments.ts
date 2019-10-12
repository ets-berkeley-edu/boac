import axios from 'axios';
import store from '@/store';
import utils from '@/api/api-utils';

export function cancel(appointmentId) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/cancel`)
    .then(response => {
      store.dispatch('user/gaAppointmentEvent', {
        id: appointmentId,
        name: `Advisor ${store.getters['user/uid']} canceled a drop-in appointment`,
        action: 'cancel'
      });
      return response.data
    }, () => null);
}

export function checkIn(appointmentId) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/check_in`)
    .then(response => {
      store.dispatch('user/gaAppointmentEvent', {
        id: appointmentId,
        name: `Advisor ${store.getters['user/uid']} checked in a drop-in appointment`,
        action: 'check_in'
      });
      return response.data
    }, () => null);
}

export function create(
    advisorDeptCodes,
    advisorName,
    advisorRole,
    advisorUid,
    details,
    sid,
    topics
) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/create`, {
      advisorDeptCodes,
      advisorName,
      advisorRole,
      advisorUid,
      details,
      sid,
      topics
    }).then(response => {
      const appointmentId = response.data.id;
      store.dispatch('user/gaAppointmentEvent', {
        id: appointmentId,
        name: `Advisor ${store.getters['user/uid']} created an appointment`,
        action: 'check_in'
      });
      return response.data
    }, () => null);
}

export function getDropInAppointmentWaitlist() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/waitlist`)
    .then(response => response.data, () => null);
}

export function getAllTopics() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/topics`)
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
