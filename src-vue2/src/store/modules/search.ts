import store from '@/store'

const state = {
  author: null,
  autocompleteInputResetKey: 0,
  domain: undefined,
  fromDate: null,
  includeAdmits: undefined,
  includeCourses: undefined,
  includeNotes: undefined,
  includeStudents: undefined,
  isFocusOnSearch: false,
  isSearching: false,
  postedBy: 'anyone',
  queryText: undefined,
  searchHistory: [],
  showAdvancedSearch: false,
  student: null,
  toDate: null,
  topic: null,
  topicOptions: []
}

const getters = {
  author: (state: any): string => state.author,
  autocompleteInputResetKey: (state: any): any => state.autocompleteInputResetKey,
  domain: (state: any): string[] => state.domain,
  fromDate: (state: any): string => state.fromDate,
  includeAdmits: (state: any): boolean => state.includeAdmits,
  includeCourses: (state: any): boolean => state.includeCourses,
  includeNotes: (state: any): boolean => state.includeNotes,
  includeStudents: (state: any): boolean => state.includeStudents,
  isDirty: (state: any): boolean => {
    const currentUser = store.getters['context/currentUser']
    return (currentUser.canAccessCanvasData && !state.includeCourses)
      || (currentUser.canAccessCanvasData && !state.includeNotes)
      || (currentUser.canAccessAdmittedStudents && !state.includeAdmits)
      || !!state.author || !!state.fromDate || state.postedBy !== 'anyone'
      || !!state.student || !!state.toDate || !!state.topic
  },
  isFocusOnSearch: (state: any): boolean => state.isFocusOnSearch,
  isSearching: (state: any): boolean => state.isSearching,
  postedBy: (state: any): string => state.postedBy,
  queryText: (state: any): string => state.queryText,
  searchHistory: (state: any): boolean => state.searchHistory,
  showAdvancedSearch: (state: any): boolean => state.showAdvancedSearch,
  student: (state: any): string => state.student,
  toDate: (state: any): string => state.toDate,
  topic: (state: any): string => state.topic,
  topicOptions: (state: any): string[] => state.topicOptions
}

const mutations = {
  resetAdvancedSearch: (state: any, queryText?: string) => {
    const currentUser = store.getters['context/currentUser']
    const domain = ['students']
    if (currentUser.canAccessCanvasData) {
      domain.push('courses')
    }
    if (currentUser.canAccessAdvisingData) {
      domain.push('notes')
    }
    if (currentUser.canAccessAdmittedStudents) {
      domain.push('admits')
    }
    state.domain = domain
    state.author = null
    state.fromDate = null
    state.postedBy = 'anyone'
    state.student = null
    state.queryText = queryText
    if (!state.queryText) {
      // Our third-party "autocomplete" component does not have a reset hook.
      // We reset its text-input by triggering a component reload with a :key change.
      state.autocompleteInputResetKey++
    }
    state.toDate = null
    state.topic = null
    state.includeAdmits = domain.includes('admits')
    state.includeCourses = domain.includes('courses')
    state.includeNotes = domain.includes('notes')
    state.includeStudents = domain.includes('students')
  },
  resetAutocompleteInput: (state: any) => state.autocompleteInputResetKey++,
  setAuthor: (state: any, value: string) => state.author = value,
  setFromDate: (state: any, value: string) => state.fromDate = value,
  setPostedBy: (state: any, value: string) => state.postedBy = value,
  setStudent: (state: any, value: string) => state.student = value,
  setToDate: (state: any, value: string) => state.toDate = value,
  setTopic: (state: any, value: string) => state.topic = value,
  setIncludeAdmits: (state: any, value: boolean) => state.includeAdmits = value,
  setIncludeCourses: (state: any, value: boolean) => state.includeCourses = value,
  setIncludeNotes: (state: any, value: boolean) => state.includeNotes = value,
  setIncludeStudents: (state: any, value: boolean) => state.includeStudents = value,
  setIsFocusOnSearch: (state: any, value: boolean) => state.isFocusOnSearch = value,
  setIsSearching: (state: any, value: boolean) => state.isSearching = value,
  setSearchHistory: (state: any, history: string[]) => state.searchHistory = history,
  setShowAdvancedSearch: (state: any, show: boolean) => state.showAdvancedSearch = show,
  setTopicOptions: (state: any, topicOptions: any[]) => state.topicOptions = topicOptions,
  setQueryText: (state: any, queryText: string) => state.queryText = queryText
}

export default {
  getters,
  mutations,
  namespaced: true,
  state
}
