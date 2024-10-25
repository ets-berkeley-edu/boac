import axios from 'axios'
import {nextTick} from 'vue'
import utils from '@/api/api-utils'
import {useContextStore} from '@/stores/context'

export function getVersion() {
  return axios.get(`${utils.apiBaseUrl()}/api/version`).then(response => response.data)
}

export function getServiceAnnouncement() {
  const url: string = `${utils.apiBaseUrl()}/api/service_announcement`
  return axios.get(url).then(response => response.data)
}

export function publishAnnouncement(publish: boolean, beforeAlertShown?: Function) {
  return axios.post(`${utils.apiBaseUrl()}/api/service_announcement/publish`, {publish}).then(response => {
    const data = response.data
    if (beforeAlertShown) {
      beforeAlertShown(publish)
    }
    nextTick(() => useContextStore().setServiceAnnouncement(data))
    return data
  })
}

export function updateAnnouncement(text: string, beforeAlertShown?: Function) {
  const url: string = `${utils.apiBaseUrl()}/api/service_announcement/update`
  return axios.post(url, {text}).then(response => {
    const data = response.data
    if (beforeAlertShown) {
      beforeAlertShown()
    }
    nextTick(() => useContextStore().setServiceAnnouncement(data))
    return data
  })
}
