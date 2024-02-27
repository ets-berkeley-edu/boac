import axios from 'axios'
import ga from '@/lib/ga'
import utils from '@/api/api-utils'

const $_track = action => ga.search(action)

export function findAdvisorsByName(query: string, limit: number, abortController: AbortController) {
  return axios
    .get(
      `${utils.apiBaseUrl()}/api/search/advisors/find_by_name?q=${query}&limit=${limit}`,
      {signal: abortController.signal}
    ).then(response => response.data)
    .catch(error => error)
}

export function getMySearchHistory() {
  const url = `${utils.apiBaseUrl()}/api/search/my_search_history`
  return axios.get(url).then(response => response.data, () => null)
}

export function addToSearchHistory(phrase: string) {
  const url = `${utils.apiBaseUrl()}/api/search/add_to_search_history`
  return axios.post(url, {phrase}).then(response => response.data, () => null)
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
  $_track(phrase)
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
  return axios
    .post(`${utils.apiBaseUrl()}/api/search/admits`, {
      searchPhrase: phrase,
      orderBy: orderBy || 'last_name',
    })
    .then(response => response.data, () => null)
}
