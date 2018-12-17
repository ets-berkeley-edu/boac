import axios from 'axios';
import store from '@/store';

export function getSection(termId, sectionId, offset, limit) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  let url = `${apiBaseUrl}/api/section/${termId}/${sectionId}`;
  if (offset || limit) {
    url += '?offset=' + (offset || 0) + '&limit=' + (limit || 50);
  }
  return axios.get(url).then(response => response.data, () => null);
}
