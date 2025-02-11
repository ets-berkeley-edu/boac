import {AxiosError, AxiosResponse, AxiosStatic} from 'axios'
import router from '@/router'
import {BoaUser} from '@/lib/types'
import {find, get, includes} from 'lodash'
import {useContextStore} from '@/stores/context'

const SKIP_REDIRECT_ON_ERROR = ['/api/user/create_or_update']

const axiosErrorHandler = (error: object, axios: AxiosStatic): void => {
  const errorStatus = get(error, 'response.status')
  const contextStore = useContextStore()
  const currentUser: BoaUser = contextStore.currentUser
  if (!axios.isCancel(error)) {
    contextStore.loadingComplete()
  }
  if (!currentUser.isAuthenticated) {
    router.push({
      path: '/',
      query: {
        m: 'Your session has expired'
      }
    })
  } else if (errorStatus === 404) {
    router.push({path: '/404'})
  } else {
    if (!axios.isCancel(error)) {
      const url = get(error, 'response.config.url')
      if (!find(SKIP_REDIRECT_ON_ERROR, path => includes(url, path))) {
        router.push({
          path: '/error',
          query: {
            m: get(error, 'response.data.message') || get(error, 'message'),
            s: errorStatus,
            t: get(error, 'response.statusText')
          }
        })
      }
    }
  }
}

export function appErrorHandler(error: object, vm: object, info: string) {
  const message = get(error, 'message') || info
  const stacktrace = get(error, 'stack', null)
  // eslint-disable-next-line no-console
  console.log(`\n${message}\n${stacktrace}\n`)
  useContextStore().setApplicationState(500, message, stacktrace)
}

export function initializeAxios(axios: AxiosStatic) {
  axios.defaults.withCredentials = true
  axios.interceptors.response.use(
    (response: AxiosResponse) => response,
    (error: AxiosError) => {
      const errorStatus = get(error, 'response.status')
      if (includes([401, 403], errorStatus)) {
        // Refresh user in case his/her session expired.
        const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL
        return axios.get(`${apiBaseUrl}/api/profile/my`).then((response: AxiosResponse) => {
          useContextStore().setCurrentUser(response.data)
          axiosErrorHandler(error, axios)
          return Promise.reject(error)
        })
      }
      axiosErrorHandler(error, axios)
      return Promise.reject(error)
    })
}
