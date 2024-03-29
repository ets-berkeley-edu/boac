<script>
import {mapActions, mapState} from 'pinia'
import {useContextStore} from '@/stores/context'
import {useSearchStore} from '@/stores/search'
import {oxfordJoin} from '@/lib/utils'

export default {
  name: 'SearchSession',
  computed: {
    ...mapState(useSearchStore, [
      'autocompleteInputResetKey',
      'domain',
      'isDirty',
      'isFocusOnSearch',
      'topicOptions'
    ]),
    author: {
      get: () => useSearchStore().postedBy === 'anyone' ? useSearchStore().author : null,
      set: function(value) {
        useSearchStore().setPostedBy('anyone')
        useSearchStore().setAuthor(value)
      }
    },
    fromDate: {
      get: () => useSearchStore().fromDate,
      set: v => useSearchStore().setFromDate(v)
    },
    labelForSearchInput: () => {
      const currentUser = useContextStore().currentUser
      const scopes = ['students']
      if (currentUser.canAccessCanvasData) {
        scopes.push('courses')
      }
      if (currentUser.canAccessAdvisingData) {
        scopes.push('notes')
      }
      const history = useSearchStore().searchHistory
      return `Search for ${oxfordJoin(scopes)}.${history && history.length ? ' Expect auto-suggest of previous searches.' : ''}`
    },
    includeAdmits: {
      get: function() {
        return this.domain.includes('admits') && useSearchStore().includeAdmits
      },
      set: v => {
        useSearchStore().setIncludeAdmits(v)
        useContextStore().alertScreenReader(`Search ${v ? 'will' : 'will not'} include admits.`)
      }
    },
    includeCourses: {
      get: () => useSearchStore().includeCourses,
      set: v => {
        useSearchStore().setIncludeCourses(v)
        useContextStore().alertScreenReader(`Search ${v ? 'will' : 'will not'} include courses.`)
      }
    },
    includeNotes: {
      get: () => useSearchStore().includeNotes,
      set: v => {
        useSearchStore().setIncludeNotes(v)
        useContextStore().alertScreenReader(`Search will include ${v ? 'notes and' : 'neither notes nor'} appointments.`)
      }
    },
    includeStudents: {
      get: () => useSearchStore().includeStudents,
      set: v => {
        useSearchStore().setIncludeStudents(v)
        useContextStore().alertScreenReader(`Search ${v ? 'will' : 'will not'} include students.`)
      }
    },
    isSearching: {
      get: () => useSearchStore().isSearching,
      set: v => useSearchStore().setIsSearching(v)
    },
    postedBy: {
      get: () => useSearchStore().postedBy,
      set: v => useSearchStore().setPostedBy(v)
    },
    queryText: {
      get: () => useSearchStore().queryText,
      set: v => useSearchStore().setQueryText(v)
    },
    showAdvancedSearch: {
      get: () => useSearchStore().showAdvancedSearch,
      set: v => useSearchStore().setShowAdvancedSearch(v)
    },
    student: {
      get: () => useSearchStore().student,
      set: v => useSearchStore().setStudent(v)
    },
    toDate: {
      get: () => useSearchStore().toDate,
      set: v => useSearchStore().setToDate(v)
    },
    topic: {
      get: () => useSearchStore().topic,
      set: v => useSearchStore().setTopic(v)
    }
  },
  methods: {
    ...mapActions(useSearchStore, [
      'resetAdvancedSearch',
      'resetAutocompleteInput',
      'setAuthor',
      'setFromDate'
    ])
  }
}
</script>
