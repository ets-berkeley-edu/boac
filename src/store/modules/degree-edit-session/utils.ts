import store from '@/store'

export function log(message: string) {
  store.getters['context/config'].isVueAppDebugMode && console.log(message)
}
