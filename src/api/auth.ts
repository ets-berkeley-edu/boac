import axios from 'axios'
import {useContextStore} from '@/stores/context'
import utils from '@/api/api-utils'

export function devAuthLogIn(uid: string, password: string) {
  const url: string = `${utils.apiBaseUrl()}/api/auth/dev_auth_login`
  return axios.post(url, {uid, password}).then(response => {
    useContextStore().setCurrentUser(response.data)
  })
}

export function getCasLoginURL() {
  return axios.get(`${utils.apiBaseUrl()}/cas/login_url`).then(response => response.data)
}

export function getCasLogoutUrl() {
  return axios.get(`${utils.apiBaseUrl()}/api/auth/logout`).then(response => response.data)
}
