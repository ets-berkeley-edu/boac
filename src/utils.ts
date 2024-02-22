import {get, includes, trim} from 'lodash'
import {useContextStore} from '@/stores/context'

const SKIP_REDIRECT_ON_ERROR = []

export function initializeAxios(app: any, axios: any) {
  const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL
  const params = new URLSearchParams(window.location.search)
  if (params.get('canvasApiDomain')) {
    axios.defaults.headers['Ripley-Canvas-Api-Domain'] = params.get('canvasApiDomain')
  }
  axios.defaults.withCredentials = true
  axios.interceptors.response.use(
    (response: any) => response.headers['content-type'] === 'application/json' ? response.data : response,
    (error: any) => {
      const errorStatus = get(error, 'response.status')
      if (includes([401, 403], errorStatus)) {
        // Refresh user in case his/her session expired.
        return axios.get(`${apiBaseUrl}/api/profile/my`).then((data: any) => {
          const currentUser = data
          useContextStore().setCurrentUser(currentUser)
          const apiUrl = trim(get(error.config, 'url'))
          const skipRedirect = currentUser.isAuthenticated || SKIP_REDIRECT_ON_ERROR.some(apiPath => apiUrl.includes(apiPath))
          if (!skipRedirect) {
            useContextStore().setApplicationState(errorStatus, 'Your session has expired')
          }
          return Promise.reject(error)
        })
      } else {
        return Promise.reject(error)
      }
    })
}
