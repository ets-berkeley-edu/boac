import axios from 'axios'
import utils from '@/api/api-utils'

export function createTopic(topic: string) {
  const url: string = `${utils.apiBaseUrl()}/api/topic/create`
  return axios.post(url, {topic}).then(response => response.data)
}

export function deleteTopic(id: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/topic/delete/${id}`)
}

export function getAllTopics(includeDeleted?: boolean) {
  const url: string = `${utils.apiBaseUrl()}/api/topics/all?includeDeleted=${includeDeleted}`
  return axios.get(url).then(response => response.data)
}

export function getTopicsForNotes(includeDeleted?: boolean) {
  const url: string = `${utils.apiBaseUrl()}/api/topics/for_notes?includeDeleted=${includeDeleted}`
  return axios.get(url).then(response => response.data)
}

export function getUsageStatistics() {
  const url: string = `${utils.apiBaseUrl()}/api/topics/usage_statistics`
  return axios.get(url).then(response => response.data)
}

export function undeleteTopic(id) {
  const url: string = `${utils.apiBaseUrl()}/api/topic/undelete`
  return axios.post(url, {id}).then(response => response.data)
}
