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

export function publishAnnouncement(publish) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/service_announcement/publish`, { publish: publish })
    .then(response => {
      const data = response.data;
      store.commit('context/storeAnnouncement', data);
      return data;
    })
    .catch(error => error);
}

export function updateAnnouncement(text) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/service_announcement/update`, { text: text })
    .then(response => {
      const data = response.data;
      store.commit('context/storeAnnouncement', data);
      return data;
    })
    .catch(error => error);
}
