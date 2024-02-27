import axios from 'axios'
import {useContextStore} from '@/stores/context'
import utils from '@/api/api-utils'

export function devAuthLogIn(uid: string, password: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/auth/dev_auth_login`, {
      uid: uid,
      password: password
    })
    .then(data => {
      useContextStore().setCurrentUser(data)
    }, error => error)
}

export function getCasLoginURL() {
  return axios
    .get(`${utils.apiBaseUrl()}/cas/login_url`)
    .then(response => response.data, () => null)
}

export function getCasLogoutUrl() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/auth/logout`)
    .then(response => response.data, () => null)
}
