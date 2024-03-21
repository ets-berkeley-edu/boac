import _ from 'lodash'
import {defineStore} from 'pinia'
import {useContextStore} from '@/stores/context'

export const useSearchStore = defineStore('search', {
  state: () => ({
    author: undefined as string | null | undefined,
    autocompleteInputResetKey: 0,
    domain: undefined as string[] | undefined,
    fromDate: undefined as string | null | undefined,
    includeAdmits: false,
    includeCourses: false,
    includeNotes: false,
    includeStudents: false,
    isDirty() {
      const currentUser = useContextStore().currentUser
      return (_.get(currentUser, 'canAccessCanvasData') && !this.includeCourses)
        || (_.get(currentUser, 'canAccessCanvasData') && !this.includeNotes)
        || (_.get(currentUser, 'canAccessAdmittedStudents') && !this.includeAdmits)
        || !!this.author || !!this.fromDate || this.postedBy !== 'anyone'
        || !!this.student || !!this.toDate || !!this.topic
    },
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
  actions: {
    resetAdvancedSearch(queryText?: string) {
      const currentUser = useContextStore().currentUser
      const domain = ['students']
      if (_.get(currentUser, 'canAccessCanvasData')) {
        domain.push('courses')
      }
      if (_.get(currentUser, 'canAccessAdvisingData')) {
        domain.push('notes')
      }
      if (_.get(currentUser, 'canAccessAdmittedStudents')) {
        domain.push('admits')
      }
      this.domain = domain
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
    setFromDate(value: string) {this.fromDate = value},
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
    setStudent(value: string) {this.student = value},
    setToDate(value: string) {this.toDate = value},
    setTopic(value: string) {this.topic = value},
    setTopicOptions(topicOptions: any[]) {this.topicOptions = topicOptions}
  }
})
