import axios from 'axios';
import store from '@/store';
import { event } from 'vue-analytics';

export function search(
  phrase: string,
  includeCourses: boolean,
  includeNotes: boolean,
  includeStudents: boolean,
  noteOptions: object,
  authorCsid: string,
  orderBy: string,
  offset: number,
  limit: number
) {
  let apiBaseUrl = store.getters['context/apiBaseUrl'];
  return axios
    .post(`${apiBaseUrl}/api/search`, {
      searchPhrase: phrase,
      students: includeStudents,
      courses: includeCourses,
      notes: includeNotes,
      noteOptions: noteOptions || {},
      authorCsid: authorCsid,
      orderBy: orderBy || 'first_name',
      offset: offset || 0,
      limit: limit || 50
    })
    .then(response => {
      event('Students', 'search', phrase, store.getters['user/user'].uid);
      return response;
    })
    .then(response => response.data, () => null);
}
