<script>
import {alertScreenReader} from '@/lib/utils'
import {labelForSearchInput} from '@/lib/search'
import {mapActions, mapState} from 'pinia'
import {useSearchStore} from '@/stores/search'

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
    labelForSearchInput,
    includeAdmits: {
      get: function() {
        return this.domain.includes('admits') && useSearchStore().includeAdmits
      },
      set: v => {
        useSearchStore().setIncludeAdmits(v)
        alertScreenReader(`Search ${v ? 'will' : 'will not'} include admits.`)
      }
    },
    includeCourses: {
      get: () => useSearchStore().includeCourses,
      set: v => {
        useSearchStore().setIncludeCourses(v)
        alertScreenReader(`Search ${v ? 'will' : 'will not'} include courses.`)
      }
    },
    includeNotes: {
      get: () => useSearchStore().includeNotes,
      set: v => {
        useSearchStore().setIncludeNotes(v)
        alertScreenReader(`Search will include ${v ? 'notes and' : 'neither notes nor'} appointments.`)
      }
    },
    includeStudents: {
      get: () => useSearchStore().includeStudents,
      set: v => {
        useSearchStore().setIncludeStudents(v)
        alertScreenReader(`Search ${v ? 'will' : 'will not'} include students.`)
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
