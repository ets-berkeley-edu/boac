import axios from 'axios'
import store from '@/store'
import utils from '@/api/api-utils'
import Vue from 'vue'
import {getServiceAnnouncement} from '@/api/config'
import {initGoogleAnalytics} from '@/lib/ga'

export function devAuthLogIn(uid: string, password: string) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/auth/dev_auth_login`, {
      uid: uid,
      password: password
    })
    .then(response => {
      store.commit('context/setCurrentUser', Vue.observable(response.data))
      initGoogleAnalytics().then(() => {
        getServiceAnnouncement().then(data => {
          store.commit('context/setServiceAnnouncement', data)
        })
      })
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
