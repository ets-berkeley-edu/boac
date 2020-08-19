import axios from 'axios';
import utils from '@/api/api-utils';

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
