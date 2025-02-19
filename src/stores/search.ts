import type {StoreDefinition} from 'pinia'
import {defineStore} from 'pinia'
import {each, isUndefined} from 'lodash'
import type {BoaUser, SelectOption} from '@/lib/types'
import {getAllTopics} from '@/api/topics'
import {useContextStore} from '@/stores/context'

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
    showAdvancedSearch: undefined as boolean | undefined,
    student: undefined as string | null | undefined,
    toDate: undefined as string | null | undefined,
    topic: undefined as string | null | undefined,
    topicOptions: [] as SelectOption<string | null>[]
  }),
  getters: {
    isDirty: (state): boolean => {
      const currentUser: BoaUser = useContextStore().currentUser
      return (currentUser.canAccessCanvasData && !state.includeCourses)
        || (currentUser.canAccessCanvasData && !state.includeNotes)
        || (currentUser.canAccessAdmittedStudents && !state.includeAdmits)
        || !!state.author || !!state.fromDate || state.postedBy !== 'anyone'
        || !!state.student || !!state.toDate || !!state.topic
    }
  },
  actions: {
    resetAdvancedSearch(queryText?: string) {
      const currentUser: BoaUser = useContextStore().currentUser
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
    setIncludeAdmits(value: boolean) {this.includeAdmits = value},
    setIncludeCourses(value: boolean) {this.includeCourses = value},
    setIncludeNotes(value: boolean) {this.includeNotes = value},
    setIncludeStudents(value: boolean) {this.includeStudents = value},
    setIsFocusOnSearch(value: boolean) {this.isFocusOnSearch = value},
    setIsSearching(value: boolean) {this.isSearching = value},
    setPostedBy(value: string) {this.postedBy = value},
    setQueryText(queryText: string) {this.queryText = queryText},
    setSearchHistory(history: string[]) {this.searchHistory = history || []},
    setShowAdvancedSearch(show: boolean, loadTopics?: boolean) {
      const fetchTopics: boolean = !!loadTopics && show && isUndefined(this.showAdvancedSearch)
      if (fetchTopics) {
        getAllTopics(true).then(rows => {
          this.topicOptions = [{text: 'Any topic', value: null}]
          each(rows, row => {
            const topic = row['topic']
            this.topicOptions.push({
              text: topic,
              value: topic
            })
          })
          this.showAdvancedSearch = show
        })
      } else {
        this.showAdvancedSearch = show
      }
    },
    setStudent(value: string | null) {this.student = value},
    setToDate(value: string | null) {this.toDate = value},
    setTopic(value: string | null) {this.topic = value}
  }
})
