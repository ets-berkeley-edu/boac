import axios from 'axios';
import utils from '@/api/api-utils';
import Vue from "vue";

export function getMySearchHistory() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/search/my_search_history`)
    .then(response => response.data, () => null);
}

export function addToSearchHistory(phrase) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/search/add_to_search_history`, { phrase })
    .then(response => response.data, () => null);
}

export function search(
  phrase: string,
  includeAppointments: boolean,
  includeCourses: boolean,
  includeNotes: boolean,
  includeStudents: boolean,
  appointmentOptions: object,
  noteOptions: object,
  orderBy?: string,
  offset?: number,
  limit?: number
) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/search`, {
      searchPhrase: phrase,
      appointments: includeAppointments,
      students: includeStudents,
      courses: includeCourses,
      notes: includeNotes,
      appointmentOptions: appointmentOptions || {},
      noteOptions: noteOptions || {},
      orderBy: orderBy || 'first_name',
      offset: offset || 0,
      limit: limit || 50
    })
    .then(response => {
      Vue.prototype.$ga.searchEvent(`Search phrase: ${phrase}`);
      return response;
    })
    .then(response => response.data, () => null);
}
