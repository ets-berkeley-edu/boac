import axios from 'axios';
import utils from '@/api/api-utils';

export function createTopic(availableInAppointments, availableInNotes, topic) {
  return axios.post(`${utils.apiBaseUrl()}/api/topic/create`, {
    availableInAppointments,
    availableInNotes,
    topic
  }).then(response => response.data, () => null);
}

export function deleteTopic(id) {
  return axios.delete(`${utils.apiBaseUrl()}/api/topic/delete/${id}`);
}

export function getAllTopics(includeDeleted?: boolean) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/topics/all?includeDeleted=${includeDeleted}`)
    .then(response => response.data, () => null);
}

export function getTopicsForAppointments(includeDeleted?: boolean) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/topics/for_appointments?includeDeleted=${includeDeleted}`)
    .then(response => response.data, () => null);
}

export function getTopicsForNotes(includeDeleted?: boolean) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/topics/for_notes?includeDeleted=${includeDeleted}`)
    .then(response => response.data, () => null);
}

export function getUsageStatistics() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/topics/usage_statistics`)
    .then(response => response.data, () => null);
}

export function undeleteTopic(id) {
  return axios.post(`${utils.apiBaseUrl()}/api/topic/undelete`, {id})
      .then(response => response.data, () => null);
}

export function updateTopic(id, availableInAppointments, availableInNotes, topic) {
  return axios.post(`${utils.apiBaseUrl()}/api/topic/update`, {
    id,
    availableInAppointments,
    availableInNotes,
    topic
  }).then(response => response.data, () => null);
}
