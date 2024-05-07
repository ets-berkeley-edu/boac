import {defineStore, StoreDefinition} from 'pinia'
import {get} from 'lodash'
import {useContextStore} from '@/stores/context'

export const useSearchStore: StoreDefinition = defineStore('search', {
  state: () => ({
    author: undefined as string | null | undefined,
    autocompleteInputResetKey: 0,
    domain: [] as string[],
    fromDate: undefined as string | null | undefined,
    includeAdmits: false,
    includeCourses: false,
    includeNotes: false,
    includeStudents: false,
    isFocusOnSearch: false,
    isSearching: false,
    postedBy: 'anyone',
    queryText: undefined as string | undefined,
    searchHistory: [] as string[],
    showAdvancedSearch: false,
    student: undefined as string | null | undefined,
    toDate: undefined as string | null | undefined,
    topic: undefined as string | null | undefined,
    topicOptions: [] as string[]
  }),
  getters: {
    isDirty: state => {
      const currentUser = useContextStore().currentUser
      return (get(currentUser, 'canAccessCanvasData') && !state.includeCourses)
        || (get(currentUser, 'canAccessCanvasData') && !state.includeNotes)
        || (get(currentUser, 'canAccessAdmittedStudents') && !state.includeAdmits)
        || !!state.author || !!state.fromDate || state.postedBy !== 'anyone'
        || !!state.student || !!state.toDate || !!state.topic
    }
  },
  actions: {
    resetAdvancedSearch(queryText?: string) {
      const currentUser = useContextStore().currentUser
      const domain = ['students']
      if (get(currentUser, 'canAccessCanvasData')) {
        domain.push('courses')
      }
      if (get(currentUser, 'canAccessAdvisingData')) {
        domain.push('notes')
      }
      if (get(currentUser, 'canAccessAdmittedStudents')) {
        domain.push('admits')
      }
      this.domain = domain || []
      this.author = null
      this.fromDate = null
      this.postedBy = 'anyone'
      this.student = null
      this.queryText = queryText
      if (!this.queryText) {
        // Our third-party "autocomplete" component does not have a reset hook.
        // We reset its text-input by triggering a component reload with a :key change.
        this.autocompleteInputResetKey++
      }
      this.toDate = null
      this.topic = null
      this.includeAdmits = domain.includes('admits')
      this.includeCourses = domain.includes('courses')
      this.includeNotes = domain.includes('notes')
      this.includeStudents = domain.includes('students')
    },
    resetAutocompleteInput() {this.autocompleteInputResetKey++},
    setAuthor(value: string | null) {this.author = value},
    setFromDate(value: string | null) {this.fromDate = value},
    setIncludeAdmits(value: boolean) {this.includeAdmits = value},
    setIncludeCourses(value: boolean) {this.includeCourses = value},
    setIncludeNotes(value: boolean) {this.includeNotes = value},
    setIncludeStudents(value: boolean) {this.includeStudents = value},
    setIsFocusOnSearch(value: boolean) {this.isFocusOnSearch = value},
    setIsSearching(value: boolean) {this.isSearching = value},
    setPostedBy(value: string) {this.postedBy = value},
    setQueryText(queryText: string) {this.queryText = queryText},
    setSearchHistory(history: string[]) {this.searchHistory = history || []},
    setShowAdvancedSearch(show: boolean) {this.showAdvancedSearch = show},
    setStudent(value: string | null) {this.student = value},
    setToDate(value: string | null) {this.toDate = value},
    setTopic(value: string | null) {this.topic = value},
    setTopicOptions(topicOptions: any[]) {this.topicOptions = topicOptions}
  }
})
