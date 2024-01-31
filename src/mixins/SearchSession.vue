<script>
import store from '@/store'
import Vue from 'vue'
import {mapGetters, mapMutations} from 'vuex'
import {oxfordJoin} from '@/utils'

export default {
  name: 'SearchSession',
  computed: {
    ...mapGetters('search', [
      'autocompleteInputResetKey',
      'domain',
      'isDirty',
      'isFocusOnSearch',
      'topicOptions'
    ]),
    author: {
      get: () => store.getters['search/postedBy'] === 'anyone' ? store.getters['search/author'] : null,
      set: function(value) {
        store.commit('search/setPostedBy', 'anyone')
        store.commit('search/setAuthor', value)
      }
    },
    fromDate: {
      get: () => store.getters['search/fromDate'],
      set: v => store.commit('search/setFromDate', v)
    },
    labelForSearchInput: () => {
      const currentUser = store.getters['context/currentUser']
      const scopes = ['students']
      if (currentUser.canAccessCanvasData) {
        scopes.push('courses')
      }
      if (currentUser.canAccessAdvisingData) {
        scopes.push('notes')
      }
      const history = store.getters['search/searchHistory']
      return `Search for ${oxfordJoin(scopes)}.${history.length ? ' Expect auto-suggest of previous searches.' : ''}`
    },
    includeAdmits: {
      get: function() {
        return this.domain.includes('admits') && store.getters['search/includeAdmits']
      },
      set: v => {
        store.commit('search/setIncludeAdmits', v)
        Vue.prototype.$announcer.polite(`Search ${v ? 'will' : 'will not'} include admits.`)
      }
    },
    includeCourses: {
      get: () => store.getters['search/includeCourses'],
      set: v => {
        store.commit('search/setIncludeCourses', v)
        Vue.prototype.$announcer.polite(`Search ${v ? 'will' : 'will not'} include courses.`)
      }
    },
    includeNotes: {
      get: () => store.getters['search/includeNotes'],
      set: v => {
        store.commit('search/setIncludeNotes', v)
        Vue.prototype.$announcer.polite(`Search will include ${v ? 'notes and' : 'neither notes nor'} appointments.`)
      }
    },
    includeStudents: {
      get: () => store.getters['search/includeStudents'],
      set: v => {
        store.commit('search/setIncludeStudents', v)
        Vue.prototype.$announcer.polite(`Search ${v ? 'will' : 'will not'} include students.`)
      }
    },
    isSearching: {
      get: () => store.getters['search/isSearching'],
      set: v => store.commit('search/setIsSearching', v)
    },
    postedBy: {
      get: () => store.getters['search/postedBy'],
      set: v => store.commit('search/setPostedBy', v)
    },
    queryText: {
      get: () => store.getters['search/queryText'],
      set: v => store.commit('search/setQueryText', v)
    },
    searchHistory: {
      get: () => store.getters['search/searchHistory'],
      set: v => store.commit('search/setSearchHistory', v)
    },
    showAdvancedSearch: {
      get: () => store.getters['search/showAdvancedSearch'],
      set: v => store.commit('search/setShowAdvancedSearch', v)
    },
    student: {
      get: () => store.getters['search/student'],
      set: v => store.commit('search/setStudent', v)
    },
    toDate: {
      get: () => store.getters['search/toDate'],
      set: v => store.commit('search/setToDate', v)
    },
    topic: {
      get: () => store.getters['search/topic'],
      set: v => store.commit('search/setTopic', v)
    }
  },
  methods: {
    ...mapMutations('search', [
      'resetAdvancedSearch',
      'resetAutocompleteInput',
      'setAuthor',
      'setFromDate',
      'setIsFocusOnSearch'
    ])
  }
}
</script>
