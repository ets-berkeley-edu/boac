import axios from 'axios';
import store from '@/store';

export function getConfig() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/config`)
    .then(response => response.data, () => null);
}

export function ping() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/ping`)
    .then(response => response.data, () => null);
}

export function getVersion() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/version`)
    .then(response => response.data, () => null);
}

export function getServiceAnnouncement() {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .get(`${apiBaseUrl}/api/service_announcement`)
    .then(response => response.data, () => null);
}

export function updateServiceAnnouncement(text, isLive) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  let data = {
    text: text,
    isLive: isLive
  };
  return axios
    .post(`${apiBaseUrl}/api/service_announcement/update`, data)
    .then(response => {
      const data = response.data;
      store.commit('context/storeServiceAnnouncement', data);
      return data;
    })
    .catch(error => error);
}
