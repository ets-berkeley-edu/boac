import cohort from '@/store/modules/cohort-edit-session'
import context from '@/store/modules/context'
import curatedGroup from '@/store/modules/curated-group'
import degreeEditSession from '@/store/modules/degree-edit-session'
import noteEditSession from '@/store/modules/note-edit-session'
import search from '@/store/modules/search'
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    cohort,
    context,
    curatedGroup,
    degreeEditSession,
    noteEditSession,
    search
  },
  strict: process.env.NODE_ENV !== 'production'
})
