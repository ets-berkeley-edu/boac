import axios from 'axios';
import store from '@/store';

export function search(phrase: string) {
  return axios
    .post(`${store.state.apiBaseUrl}/api/students/search`, {
      searchPhrase: phrase
    })
    .then(response => response.data, () => null);
}
