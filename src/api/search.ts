import axios from 'axios';
import store from '@/store';
import utils from '@/api/api-utils';

export function search(
  phrase: string,
  includeCourses: boolean,
  includeNotes: boolean,
  includeStudents: boolean,
  noteOptions: object,
  orderBy: string,
  offset: number,
  limit: number
) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/search`, {
      searchPhrase: phrase,
      students: includeStudents,
      courses: includeCourses,
      notes: includeNotes,
      noteOptions: noteOptions || {},
      orderBy: orderBy || 'first_name',
      offset: offset || 0,
      limit: limit || 50
    })
    .then(response => {
      store.dispatch('user/gaSearchEvent', {
        action: 'search',
        name: `Search phrase: ${phrase}`
      });
      return response;
    })
    .then(response => response.data, () => null);
}
