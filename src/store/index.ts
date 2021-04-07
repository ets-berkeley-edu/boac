import cohortEditSession from '@/store/modules/cohort-edit-session'
import context from '@/store/modules/context'
import curatedEditSession from '@/store/modules/curated-edit-session'
import currentUserExtras from '@/store/modules/current-user-extras'
import degreeEditSession from '@/store/modules/degree-edit-session'
import noteEditSession from '@/store/modules/note-edit-session'
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    cohortEditSession,
    context,
    curatedEditSession,
    currentUserExtras,
    degreeEditSession,
    noteEditSession
  },
  strict: process.env.NODE_ENV !== 'production'
})
