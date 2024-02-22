import mitt from 'mitt'
import {defineStore} from 'pinia'

export const useContextStore = defineStore('context', {
  state: () => ({
    config: undefined,
    currentUser: {},
    eventHub: mitt()
  }),
  actions: {
    setConfig(config: any) {
      this.config = config
    },
    setCurrentUser(user: any) {
      this.currentUser = user
      this.eventHub.emit('current-user-update')
    }
  }
})
