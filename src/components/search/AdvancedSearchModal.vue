<template>
  <v-tooltip aria-label="Advanced search options" location="bottom" text="Advanced search options">
    <template #activator="{props}">
      <v-btn
        id="search-options-panel-toggle"
        v-bind="props"
        class="mx-1"
        :class="{'border-0': !isFocusAdvSearchButton}"
        color="white"
        :disabled="searchStore.isSearching"
        height="46"
        min-height="46"
        min-width="46"
        variant="text"
        width="46"
        @click="openAdvancedSearch"
        @focusin="() => isFocusAdvSearchButton = true"
        @focusout="() => isFocusAdvSearchButton = false"
      >
        <span class="sr-only">Open advanced search</span>
        <v-icon :icon="mdiTune" size="large" />
      </v-btn>
    </template>
  </v-tooltip>
  <v-dialog
    id="advanced-search-modal"
    aria-labelledby="advanced-search-header"
    persistent
    scrollable
    :model-value="searchStore.showAdvancedSearch"
    @update:model-value="searchStore.setShowAdvancedSearch"
  >
    <v-card
      class="modal-content"
      :class="{'modal-fullscreen': $vuetify.display.smAndDown}"
      max-width="800"
      min-width="700"
      width="80%"
    >
      <FocusLock :disabled="isFocusLockDisabled" @keydown.esc="cancel">
        <v-card-title>
          <AdvancedSearchModalHeader :on-click-close="cancel" />
        </v-card-title>
        <v-card-text class="modal-body">
          <div class="pb-4">
            <label for="advanced-search-students-input" class="sr-only">{{ labelForSearchInput() }}</label>
            <v-combobox
              id="advanced-search-students-input"
              :key="searchStore.autocompleteInputResetKey"
              v-model="model.queryText"
              :aria-required="searchInputRequired"
              autocomplete="off"
              clearable
              density="comfortable"
              :disabled="searchStore.isSearching"
              hide-details
              hide-no-data
              :items="searchStore.searchHistory"
              :menu-icon="null"
              persistent-clear
              placeholder="Search"
              type="search"
              variant="outlined"
              @keydown.enter="search"
              @update:menu="isOpen => isFocusLockDisabled = isOpen"
            />
          </div>
          <div class="font-size-16 font-weight-bold">
            What is the extent of your search?
            <span
              v-if="!model.includeAdmits && !model.includeStudents && !model.includeCourses && !model.includeNotes"
              class="text-error"
            >
              Please select one or more.
            </span>
          </div>
          <div class="align-center d-flex flex-wrap">
            <v-checkbox
              v-if="currentUser.canAccessAdmittedStudents"
              id="search-include-admits-checkbox"
              v-model="model.includeAdmits"
              color="primary"
              hide-details
              label="Students"
            >
              <template #label>
                <span class="sr-only">Search for </span>Admitted Students
              </template>
            </v-checkbox>
            <v-checkbox
              id="search-include-students-checkbox"
              v-model="model.includeStudents"
              color="primary"
              hide-details
            >
              <template #label>
                <span class="sr-only">Search for </span>Students
              </template>
            </v-checkbox>
            <v-checkbox
              v-if="currentUser.canAccessCanvasData"
              id="search-include-courses-checkbox"
              v-model="model.includeCourses"
              color="primary"
              hide-details
            >
              <template #label>
                <span class="sr-only">Search for </span>Classes
              </template>
            </v-checkbox>
            <v-checkbox
              v-if="currentUser.canAccessAdvisingData"
              id="search-include-notes-checkbox"
              v-model="model.includeNotes"
              aria-controls="search-option-note-filters"
              :aria-expanded="model.includeNotes"
              color="primary"
              hide-details
              @change="onChangeIncludeNotes"
            >
              <template #label>
                <span class="sr-only">Search for</span>
                Notes &amp; Appointments
              </template>
            </v-checkbox>
          </div>
          <v-expand-transition v-if="currentUser.canAccessAdvisingData">
            <v-card
              v-show="model.includeNotes"
              id="search-option-note-filters"
              color="primary"
              min-width="350"
              variant="outlined"
            >
              <v-card-title>
                <h3 class="notes-and-appointments-filters-header">Filters for notes and appointments</h3>
              </v-card-title>
              <v-card-text class="w-75" :class="{'w-100': $vuetify.display.smAndDown}">
                <div class="px-3">
                  <label class="form-control-label" for="search-option-note-filters-topic">Topic</label>
                  <div>
                    <select
                      id="search-option-note-filters-topic"
                      v-model="model.topic"
                      class="ml-0 my-2 select-menu w-75"
                      :class="{'w-100': $vuetify.display.xs}"
                      :disabled="searchStore.isSearching"
                    >
                      <option
                        v-for="topic in searchStore.topicOptions"
                        :id="`search-notes-by-topic-${normalizeId(topic.value)}`"
                        :key="topic.value"
                        :aria-label="`Add topic ${topic.text}`"
                        :value="topic.value"
                      >
                        {{ topic.text }}
                      </option>
                    </select>
                  </div>
                  <div class="pt-4">
                    <label class="form-control-label" for="note-filters-posted-by">Posted By</label>
                    <v-radio-group
                      id="note-filters-posted-by"
                      v-model="model.postedBy"
                      hide-details
                      inline
                    >
                      <v-radio
                        id="search-options-note-filters-posted-by-anyone"
                        :disabled="searchStore.isSearching"
                        :ischecked="model.postedBy === 'anyone'"
                        label="Anyone"
                        value="anyone"
                      />
                      <v-radio
                        id="search-options-note-filters-posted-by-you"
                        :disabled="searchStore.isSearching"
                        :ischecked="model.postedBy === 'you'"
                        label="You"
                        value="you"
                        @change="() => model.author = null"
                      />
                      <v-radio
                        id="search-options-note-filters-posted-by-your department"
                        :disabled="searchStore.isSearching"
                        :ischecked="model.postedBy === 'yourDepartment'"
                        label="Your Department(s)"
                        value="yourDepartment"
                      />
                    </v-radio-group>
                  </div>
                  <div class="pt-2 w-75" :class="{'w-100': $vuetify.display.xs}">
                    <label class="form-control-label" for="search-options-note-filters-author">Advisor</label>
                    <span id="notes-search-author-input-label" class="sr-only">
                      Select note author from list of suggested advisors.
                    </span>
                    <v-autocomplete
                      id="search-options-note-filters-author"
                      autocomplete="off"
                      :clearable="!isFetchingAdvisors"
                      class="mt-1"
                      :class="{'demo-mode-blur': currentUser.inDemoMode}"
                      color="primary"
                      density="compact"
                      :disabled="searchStore.isSearching || model.postedBy === 'you' || model.postedBy === 'yourDepartment'"
                      hide-details
                      hide-no-data
                      :items="suggestedAdvisors"
                      :maxlength="56"
                      :menu-icon="null"
                      min-width="12rem"
                      :model-value="model.postedBy === 'anyone' ? model.author : null"
                      placeholder="Enter name..."
                      variant="outlined"
                      @click:clear="onClearAdvisorSearch"
                      @update:menu="isOpen => isFocusLockDisabled = isOpen"
                      @update:model-value="author => {
                        model.postedBy = 'anyone'
                        model.author = author
                      }"
                      @update:search="onUpdateAdvisorSearch"
                    >
                      <template #append-inner>
                        <v-progress-circular
                          v-if="isFetchingAdvisors"
                          color="pale-blue"
                          indeterminate
                          :size="16"
                          :width="3"
                        />
                      </template>
                      <template #selection>
                        {{ model.author.label }}
                      </template>
                    </v-autocomplete>
                  </div>
                  <div class="pt-3 w-75" :class="{'w-100': $vuetify.display.xs}">
                    <label class="form-control-label" for="search-options-note-filters-student">
                      <span aria-hidden="true">Student (name or SID)</span>
                      <span class="sr-only">Student (name or S I D)</span>
                    </label>
                    <span id="notes-search-student-input-label" class="sr-only">
                      Select a student for notes-related search. Expect auto-suggest as you type name or SID.
                    </span>
                    <v-autocomplete
                      id="search-options-note-filters-student"
                      autocomplete="off"
                      :clearable="!isFetchingStudents"
                      class="mt-1"
                      :class="{'demo-mode-blur': currentUser.inDemoMode}"
                      color="primary"
                      density="compact"
                      :disabled="searchStore.isSearching"
                      hide-details
                      hide-no-data
                      :items="suggestedStudents"
                      :maxlength="56"
                      :menu-icon="null"
                      min-width="12rem"
                      :model-value="model.student"
                      placeholder="Enter name or SID..."
                      variant="outlined"
                      @click:clear="onClearStudentSearch"
                      @update:menu="isOpen => isFocusLockDisabled = isOpen"
                      @update:model-value="student => model.student = student"
                      @update:search="onUpdateStudentSearch"
                    >
                      <template #append-inner>
                        <v-progress-circular
                          v-if="isFetchingAdvisors"
                          color="pale-blue"
                          indeterminate
                          :size="16"
                          :width="3"
                        />
                      </template>
                      <template #selection>
                        {{ model.student.label }}
                      </template>
                    </v-autocomplete>
                  </div>
                  <div class="pt-3">
                    <label id="search-options-date-range-label" class="form-control-label">
                      Date Range
                    </label>
                    <div class="d-flex flex-wrap mt-1">
                      <div class="d-flex align-center justify-end pb-2">
                        <label
                          id="search-options-from-date-label"
                          class="text-black date-range-label"
                          for="search-options-from-date-input"
                        >
                          <span aria-hidden="true">From</span>
                          <span class="sr-only">date range: <q>begin</q> date.</span>
                          <span class="sr-only">Format: M M slash D D slash Y Y Y Y.</span>
                        </label>
                        <AccessibleDateInput
                          aria-label="Begin date"
                          container-id="advanced-search-modal"
                          :get-value="() => model.fromDate"
                          id-prefix="search-options-from-date"
                          :max-date="model.toDate || new Date()"
                          :set-value="fromDate => model.fromDate = fromDate"
                        />
                      </div>
                      <div class="d-flex align-center justify-end pb-2">
                        <label
                          id="search-options-to-date-label"
                          class="text-black date-range-label d-flex justify-center"
                          for="search-options-to-date-input"
                        >
                          <span aria-hidden="true">To</span>
                          <span class="sr-only">date range: <q>end</q> date.</span>
                          <span class="sr-only">Format: M M slash D D slash Y Y Y Y.</span>
                        </label>
                        <AccessibleDateInput
                          aria-label="End date"
                          container-id="advanced-search-modal"
                          :get-value="() => model.toDate"
                          id-prefix="search-options-to-date"
                          :max-date="new Date()"
                          :min-date="model.fromDate"
                          :set-value="toDate => model.toDate = toDate"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-expand-transition>
        </v-card-text>
        <v-card-actions class="modal-footer">
          <div class="flex-grow-1">
            <v-btn
              v-if="model.includeNotes && searchStore.isDirty"
              id="reset-advanced-search-form-btn"
              :disabled="searchStore.isSearching"
              text="Reset"
              variant="text"
              @click="() => reset(true)"
            />
          </div>
          <ProgressButton
            id="advanced-search"
            :action="search"
            :disabled="isSearchDisabled"
            :in-progress="searchStore.isSearching"
            :text="searchStore.isSearching ? 'Searching...' : 'Search'"
          />
          <v-btn
            id="advanced-search-cancel"
            :disabled="searchStore.isSearching"
            text="Cancel"
            variant="text"
            @click="cancel"
          />
        </v-card-actions>
      </FocusLock>
    </v-card>
  </v-dialog>
</template>

<script setup>
import AccessibleDateInput from '@/components/util/AccessibleDateInput'
import AdvancedSearchModalHeader from '@/components/search/AdvancedSearchModalHeader'
import FocusLock from 'vue-focus-lock'
import ProgressButton from '@/components/util/ProgressButton'
import router from '@/router'
import {addToSearchHistory, findAdvisorsByName} from '@/api/search'
import {alertScreenReader, normalizeId, putFocusNextTick, scrollToTop} from '@/lib/utils'
import {computed, ref, watch} from 'vue'
import {DateTime} from 'luxon'
import {debounce, isDate, map, size, trim} from 'lodash'
import {findStudentsByNameOrSid} from '@/api/student'
import {labelForSearchInput} from '@/lib/search'
import {mdiTune} from '@mdi/js'
import {useContextStore} from '@/stores/context'
import {useSearchStore} from '@/stores/search'

const getDefaultModel = () => ({
  author: undefined,
  fromDate: undefined,
  includeAdmits: undefined,
  includeCourses: undefined,
  includeNotes: undefined,
  includeStudents: undefined,
  postedBy: undefined,
  student: undefined,
  toDate: undefined,
  topic: undefined,
  queryText: ''
})

const contextStore = useContextStore()
const searchStore = useSearchStore()
const currentUser = contextStore.currentUser

const counter = ref(0)
const isFocusAdvSearchButton = ref(false)
const isFocusLockDisabled = ref(false)
const isFetchingAdvisors = ref(false)
const isFetchingStudents = ref(false)
const suggestedAdvisors = ref([])
const suggestedStudents = ref([])

const allOptionsUnchecked = computed(() => {
  const m = model.value
  return (!currentUser.canAccessAdmittedStudents || !m.includeAdmits) && !m.includeCourses && !m.includeNotes && !m.includeStudents
})
const isSearchDisabled = computed(() => {
  return (
    searchStore.isSearching || allOptionsUnchecked.value ||
    (searchInputRequired.value && !trim(model.value.queryText)) ||
    !validDateRange.value
  )
})
const model = ref(getDefaultModel())
const searchInputRequired = computed(() => {
  const m = model.value
  return !m.includeNotes || !(m.author || m.fromDate || m.toDate || m.postedBy !== 'anyone' || m.student || m.topic)
})
const validDateRange = computed(() => {
  const m = model.value
  if (isDate(m.fromDate) && isDate(m.toDate) && (m.toDate < m.fromDate)) {
    return false
  } else {
    return (!m.fromDate || isDate(m.fromDate)) && (!m.toDate || isDate(m.toDate))
  }
})

watch(() => searchStore.showAdvancedSearch, show => {
  if (show) {
    model.value = {
      author: searchStore.author,
      fromDate: searchStore.fromDate,
      includeAdmits: searchStore.includeAdmits,
      includeCourses: searchStore.includeCourses,
      includeNotes: searchStore.includeNotes,
      includeStudents: searchStore.includeStudents,
      postedBy: searchStore.postedBy,
      queryText: searchStore.queryText,
      student: searchStore.student,
      toDate: searchStore.toDate,
      topic: searchStore.topic
    }
    putFocusNextTick('advanced-search-close')
  } else {
    searchStore.resetAutocompleteInput()
    suggestedAdvisors.value = []
    suggestedStudents.value = []
    alertScreenReader('Closed advanced search')
    putFocusNextTick('search-options-panel-toggle')
  }
})

watch(() => model.value.postedBy, () => suggestedAdvisors.value = [])

const cancel = () => {
  searchStore.setShowAdvancedSearch(false)
  searchStore.resetAutocompleteInput()
  setTimeout(() => reset(false), 100)
}

const onChangeIncludeNotes = checked => {
  if (!checked) {
    model.value.author = model.value.fromDate = model.value.student = model.value.toDate = model.value.topic = null
    model.value.postedBy = 'anyone'
  }
}

const onClearAdvisorSearch = () => {
  suggestedAdvisors.value = []
  isFetchingAdvisors.value = false
}

const onClearStudentSearch = () => {
  suggestedStudents.value = []
  isFetchingStudents.value = false
}

const onUpdateAdvisorSearch = debounce(query => {
  const q = trim(query)
  if (size(q) > 1) {
    isFetchingAdvisors.value = true
    findAdvisorsByName(q, 20, new AbortController()).then(results => {
      suggestedAdvisors.value = map(results, result => ({title: result.label, value: result}))
      isFetchingAdvisors.value = false
    })
  }
}, 500)

const onUpdateStudentSearch = debounce(query => {
  const q = trim(query)
  if (size(q) > 1) {
    isFetchingStudents.value = true
    findStudentsByNameOrSid(q, 20, new AbortController()).then(results => {
      suggestedStudents.value = map(results, result => ({title: result.label, value: result}))
      isFetchingStudents.value = false
    })
  }
}, 500)

const openAdvancedSearch = () => {
  searchStore.setShowAdvancedSearch(true)
}

const reset = force => {
  if (force || !window.location.pathname.startsWith('/search')) {
    searchStore.resetAdvancedSearch(searchStore.queryText)
  }
}

const search = () => {
  const m = model.value
  const q = trim(m.queryText)
  if (q || !searchInputRequired.value) {
    // Transfer contents of the model object to the Pinia store.
    searchStore.setAuthor(m.author)
    searchStore.setFromDate(m.fromDate)
    searchStore.setIncludeAdmits(m.includeAdmits)
    searchStore.setIncludeCourses(m.includeCourses)
    searchStore.setIncludeNotes(m.includeNotes)
    searchStore.setIncludeStudents(m.includeStudents)
    searchStore.setPostedBy(m.postedBy)
    searchStore.setQueryText(q)
    searchStore.setStudent(m.student)
    searchStore.setToDate(m.toDate)
    searchStore.setTopic(m.topic)

    // Next, do the search.
    searchStore.setIsSearching(true)
    const query = {
      _: counter.value++,
      notes: searchStore.includeNotes,
      students: searchStore.includeStudents
    }
    if (searchStore.includeAdmits) {
      query.admits = searchStore.includeAdmits
    }
    if (searchStore.includeCourses) {
      query.courses = searchStore.includeCourses
    }
    if (q) {
      query.q = q
    }
    if (searchStore.includeNotes) {
      if (searchStore.postedBy === 'you') {
        query.advisorCsid = currentUser.csid
      } else if (searchStore.author) {
        query.advisorCsid = searchStore.author.sid
        query.advisorUid = searchStore.author.uid
      } else if (searchStore.postedBy === 'yourDepartment') {
        if (currentUser.departments && currentUser.departments.length > 0) {
          query.departmentCodes = currentUser.departments.map((department) => department.code)
        }
      }
      if (searchStore.student) {
        query.studentCsid = searchStore.student.sid
      }
      if (searchStore.topic) {
        query.noteTopic = searchStore.topic
      }
      if (searchStore.fromDate) {
        query.noteDateFrom = DateTime.fromJSDate(searchStore.fromDate).toFormat('yyyy-MM-dd')
      }
      if (searchStore.toDate) {
        query.noteDateTo = DateTime.fromJSDate(searchStore.toDate).toFormat('yyyy-MM-dd')
      }
    }
    router.push({path: '/search', query: query}).then(() => {
      searchStore.setShowAdvancedSearch(false)
      searchStore.setIsSearching(false)
    })
    if (q) {
      addToSearchHistory(q).then(history => {
        searchStore.searchHistory = history
      })
    }
  } else {
    alertScreenReader('Search input is required')
    putFocusNextTick('search-students-input')
  }
  scrollToTop()
}
</script>

<style scoped>
.date-range-label {
  width: 3rem;
}
.form-control-label {
  color: rgb(var(--v-theme-on-surface));
  font-size: 16px;
  font-weight: bold;
}
.notes-and-appointments-filters-header {
  color: rgb(var(--v-theme-primary));
  font-size: 18px;
  font-weight: bolder;
}
</style>
