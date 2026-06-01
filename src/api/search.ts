import axios from 'axios'
import ga from '@/lib/ga'
import utils from '@/api/api-utils'

const $_track = action => ga.search(action)

export function findAdvisorsByName(query: string, limit: number, abortController: AbortController) {
  const url: string = `${utils.apiBaseUrl()}/api/search/advisors/find_by_name?q=${query}&limit=${limit}`
  return axios.get(url, {signal: abortController.signal}).then(response => response.data)
}

export function getMySearchHistory() {
  const url: string = `${utils.apiBaseUrl()}/api/search/my_search_history`
  return axios.get(url).then(response => response.data)
}

export function addToSearchHistory(phrase: string) {
  const url: string = `${utils.apiBaseUrl()}/api/search/add_to_search_history`
  return axios.post(url, {phrase}).then(response => response.data)
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
  limit?: number,
  includeEforms?: boolean,
  eformOptions?: object
) {
  $_track(phrase)
  const includeAdvisingDomains = includeNotes || includeAppointments || !!includeEforms
  return axios
    .post(`${utils.apiBaseUrl()}/api/search`, {
      searchPhrase: phrase,
      appointments: includeAppointments,
      students: includeStudents,
      courses: includeCourses,
      notes: includeNotes,
      eForms: includeEforms ?? includeAdvisingDomains,
      appointmentOptions: appointmentOptions || {},
      noteOptions: noteOptions || {},
      eformOptions: eformOptions || appointmentOptions || {},
      orderBy: orderBy || 'first_name',
      offset: offset || 0,
      limit: limit || 50
    })
    .then(response => response.data)
}

export function peerAdvisorSearch(phrase: string, peerAdvisingDepartmentId: number, offset: number, limit: number, peerAdvisorUid: string, showMyNotesOnly = false, notes = true, students = true) {
    $_track(phrase)
    const data = {
      searchPhrase: phrase,
      peerAdvisingDepartmentId: peerAdvisingDepartmentId,
      offset: offset || 0,
      limit: limit || 50,
      peerAdvisorUid: showMyNotesOnly ? peerAdvisorUid : null,
      students: students,
      notes: notes
    }
    return axios
    .post(`${utils.apiBaseUrl()}/api/search/peer_advising_notes`, data)
    .then(response => response.data)
}

export function searchAdmittedStudents(phrase: string, orderBy?: string) {
  const url: string = `${utils.apiBaseUrl()}/api/search/admits`
  const data = {searchPhrase: phrase, orderBy: orderBy || 'last_name'}
  return axios.post(url, data).then(response => response.data)
}
