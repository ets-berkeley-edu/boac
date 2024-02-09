import store from '@/store'
import {deleteDegreeCategory, deleteDegreeCourse, getDegreeTemplate} from '@/api/degree'

export function deleteCategory(categoryId: number) {
  return new Promise(resolve => {
    const templateId: number = store.getters['degree/templateId']
    deleteDegreeCategory(categoryId).then(() => refreshDegreeTemplate(templateId)).then(resolve)
  })
}

export function deleteCourse(courseId: number): Promise<any> {
  return new Promise(resolve => {
    const templateId: number = store.getters['degree/templateId']
    deleteDegreeCourse(courseId).then(() => refreshDegreeTemplate(templateId)).then(resolve)
  })
}

export function log(message: string) {
  store.getters['context/config'].isVueAppDebugMode && console.log(message)
}

export function refreshDegreeTemplate(templateId: number) {
  return new Promise<void>(resolve => {
    getDegreeTemplate(templateId).then((template: any) => {
      store.commit('degree/resetSession', template)
      return resolve()
    })
  })
}
