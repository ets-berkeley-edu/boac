import router from '@/router'
import {get, find, includes} from 'lodash'
import {useContextStore} from '@/stores/context'

const SKIP_REDIRECT_ON_ERROR = ['/api/user/create_or_update']

const axiosErrorHandler = (error, axios) => {
  const errorStatus = get(error, 'response.status')
  const currentUser = useContextStore().currentUser
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
            m: get(error, 'response.data.message') || error.message,
            s: errorStatus,
            t: get(error, 'response.statusText')
          }
        })
      }
    }
  }
}
export function initializeAxios(app: any, axios: any) {
  axios.defaults.withCredentials = true
  axios.interceptors.response.use(
    (response: any) => response.headers['content-type'] === 'application/json' ? response.data : response,
    (error: any) => {
      const errorStatus = get(error, 'response.status')
      if (includes([401, 403], errorStatus)) {
        // Refresh user in case his/her session expired.
        const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL
        return axios.get(`${apiBaseUrl}/api/profile/my`).then((user: any) => {
          useContextStore().setCurrentUser(user)
          axiosErrorHandler(error, axios)
          return Promise.reject(error)
        })
      }
      axiosErrorHandler(error, axios)
      return Promise.reject(error)
    })
}
