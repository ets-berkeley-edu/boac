import axios from 'axios'
import utils from '@/api/api-utils'
import Vue from 'vue'

let $_findAdvisorsByNameCancel = axios.CancelToken.source()

const $_track = (action, label?) => Vue.prototype.$ga.search(action, label)

export function findAdvisorsByName(query: string, limit: number) {
  if ($_findAdvisorsByNameCancel) {
     $_findAdvisorsByNameCancel.cancel()
  }
  $_findAdvisorsByNameCancel = axios.CancelToken.source()
  return axios
    .get(
      `${utils.apiBaseUrl()}/api/search/advisors/find_by_name?q=${query}&limit=${limit}`,
      {cancelToken: $_findAdvisorsByNameCancel.token}
    ).then(response => response.data)
    .catch(error => error)
}

export function getMySearchHistory() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/search/my_search_history`)
    .then(response => response.data, () => null)
}

export function addToSearchHistory(phrase) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/search/add_to_search_history`, {phrase})
    .then(response => response.data, () => null)
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
  $_track('search', phrase)
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
    .then(response => response.data, () => null)
}

export function searchAdmittedStudents(phrase: string, orderBy?: string) {
  $_track('admits', phrase)
  return axios
    .post(`${utils.apiBaseUrl()}/api/search/admits`, {
      searchPhrase: phrase,
      orderBy: orderBy || 'last_name',
    })
    .then(response => response.data, () => null)
}
