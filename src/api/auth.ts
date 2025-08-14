import axios from 'axios'
import utils from '@/api/api-utils'
import {initGoogleAnalytics} from '@/lib/ga'
import {useContextStore} from '@/stores/context'

export function devAuthLogIn(uid: string, password: string): Promise<void> {
  // eslint-disable-next-line no-async-promise-executor
  return new Promise(async (resolve, reject) => {
    try {
      const url: string = `${utils.apiBaseUrl()}/api/auth/dev_auth_login`
      await axios.post(url, {uid, password}).then(response => {
        useContextStore().setCurrentUser(response.data).then(() => {
          initGoogleAnalytics()
          resolve()
        })
      })
    } catch (error) {
      reject(error)
    }
  })
}

export function getCasLoginURL() {
  return axios.get(`${utils.apiBaseUrl()}/cas/login_url`).then(response => response.data)
}

export function getCasLogoutUrl() {
  return axios.get(`${utils.apiBaseUrl()}/api/auth/logout`).then(response => response.data)
}
