import axios from 'axios';
import store from '@/store';
import utils from '@/api/api-utils';

export function getAppointment(appointmentId) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointment/${appointmentId}`)
    .then(response => response.data, () => null);
}

export function markRead(appointmentId) {
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
