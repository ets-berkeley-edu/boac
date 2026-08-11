import type {AxiosError, AxiosResponse, AxiosStatic, InternalAxiosRequestConfig} from 'axios'
import type {ComponentPublicInstance} from 'vue'
import {find, get, includes} from 'lodash'
import router from '@/router'
import type {BoaUser} from '@/lib/types'
import {useContextStore} from '@/stores/context'

const SKIP_REDIRECT_ON_ERROR = ['/api/user/create_or_update', '/api/peer_advising/create_peer_advisor']
// Flask-WTF's default header names; matched on the backend by WTF_CSRF_HEADERS.
const CSRF_HEADER = 'X-CSRFToken'
// Flask-WTF's CSRFProtect only validates these methods; matching here avoids sending the header needlessly.
const CSRF_PROTECTED_METHODS = ['delete', 'patch', 'post', 'put']

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
            c: get(error, 'response.data.error_class'),
            m: get(error, 'response.data.message') || get(error, 'message'),
            s: errorStatus,
            t: get(error, 'response.statusText')
          }
        })
      }
    }
  }
}

export function appErrorHandler(error: unknown, instance: ComponentPublicInstance | null, info: string) {
  const message = get(error, 'message') || info
  const stacktrace = get(error, 'stack', null)
  // eslint-disable-next-line no-console
  console.log(`\n${message}\n${stacktrace}\n`)
  useContextStore().setApplicationState(500, message, stacktrace)
}

export function initializeAxios(axios: AxiosStatic) {
  axios.defaults.withCredentials = true
  axios.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const method = (config.method || 'get').toLowerCase()
    if (includes(CSRF_PROTECTED_METHODS, method)) {
      // Fetch CSRF token at boot (see /api/config) and cache in the context store.
      const csrfToken = useContextStore().config.csrfToken
      if (csrfToken) {
        config.headers.set(CSRF_HEADER, csrfToken)
      }
    }
    return config
  })
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
