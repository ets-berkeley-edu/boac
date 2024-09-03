import {defineStore, StoreDefinition} from 'pinia'
import {useContextStore} from '@/stores/context'
import {alertScreenReader} from '@/lib/utils'

export const useSearchStore: StoreDefinition = defineStore('search', {
  state: () => ({
    author: undefined as string | null | undefined,
    autocompleteInputResetKey: 0,
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
    isDirty: (state: any): boolean => {
      const currentUser = useContextStore().currentUser
      return (currentUser.canAccessCanvasData && !state.includeCourses)
        || (currentUser.canAccessCanvasData && !state.includeNotes)
        || (currentUser.canAccessAdmittedStudents && !state.includeAdmits)
        || !!state.author || !!state.fromDate || state.postedBy !== 'anyone'
        || !!state.student || !!state.toDate || !!state.topic
    }
  },
  actions: {
    resetAdvancedSearch(queryText?: string) {
      const currentUser = useContextStore().currentUser
      this.author = null
      this.fromDate = null
      this.postedBy = 'anyone'
      this.student = null
      this.queryText = queryText || ''
      if (!this.queryText) {
        // Our third-party "autocomplete" component does not have a reset hook.
        // We reset its text-input by triggering a component reload with a :key change.
        this.autocompleteInputResetKey++
      }
      this.toDate = null
      this.topic = null
      this.includeAdmits = currentUser.canAccessAdmittedStudents
      this.includeCourses = currentUser.canAccessCanvasData
      this.includeNotes = currentUser.canAccessAdvisingData
      this.includeStudents = true
    },
    resetAutocompleteInput() {this.autocompleteInputResetKey++},
    setAuthor(value: string | null) {this.author = value},
    setFromDate(value: string | null) {this.fromDate = value},
    setIncludeAdmits(value: boolean) {
      this.includeAdmits = value
      alertScreenReader(`Search ${value ? 'will' : 'will not'} include admits.`)
    },
    setIncludeCourses(value: boolean) {
      this.includeCourses = value
      alertScreenReader(`Search ${value ? 'will' : 'will not'} include courses.`)
    },
    setIncludeNotes(value: boolean) {
      this.includeNotes = value
      alertScreenReader(`Search will include ${value ? 'notes and' : 'neither notes nor'} appointments.`)
    },
    setIncludeStudents(value: boolean) {
      this.includeStudents = value
      alertScreenReader(`Search ${value ? 'will' : 'will not'} include students.`)
    },
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
