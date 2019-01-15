import axios from 'axios';
import store from '@/store';

export function getSection(termId, sectionId, offset, limit, featured) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  let url = `${apiBaseUrl}/api/section/${termId}/${sectionId}`;
  let params: string[] = [];
  if (offset || limit) {
    params.push('offset=' + (offset || 0) + '&limit=' + (limit || 50));
  }
  if (featured) {
    params.push('featured=' + featured);
  }
  if (params.length) {
    url += '?' + params.join('&');
  }
  return axios.get(url).then(response => response.data, () => null);
}
