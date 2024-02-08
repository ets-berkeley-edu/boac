import store from '@/store'
import {getDegreeTemplate} from '@/api/degree'

export function log(message: string) {
  store.getters['context/config'].isVueAppDebugMode && console.log(message)
}

export function refreshDegreeTemplate(templateId: number) {
  return new Promise<void>(resolve => {
    getDegreeTemplate(templateId).then((template: any) => {
      store.commit('degreeEditSession/resetSession', template)
      return resolve()
    })
  })
}
