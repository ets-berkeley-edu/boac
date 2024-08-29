<template>
  <v-tooltip location="bottom" text="Advanced search options">
    <template #activator="{props}">
      <v-btn
        id="search-options-panel-toggle"
        v-bind="props"
        class="pl-0"
        :class="{'border-0': !isFocusAdvSearchButton}"
        color="white"
        :disabled="searchStore.isSearching"
        variant="text"
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
    v-model="showAdvancedSearchModel"
    aria-labelledby="advanced-search-header"
    persistent
  >
    <v-card
      class="modal-content"
      max-width="800"
      min-width="700"
      width="80%"
    >
      <FocusLock @keydown.esc="cancel">
        <v-card-title>
          <AdvancedSearchModalHeader :on-click-close="cancel" />
        </v-card-title>
        <v-card-text class="modal-body">
          <div class="pb-4">
            <label for="advanced-search-students-input" class="sr-only">{{ labelForSearchInput() }}</label>
            <v-combobox
              id="advanced-search-students-input"
              :key="searchStore.autocompleteInputResetKey"
              v-model="queryTextModel"
              :aria-required="searchInputRequired"
              autocomplete="off"
              clearable
              density="comfortable"
              :disabled="searchStore.isSearching"
              hide-details
              hide-no-data
              :items="searchStore.searchHistory"
              :menu-icon="null"
              :menu-props="{'attach': false, 'location': 'bottom'}"
              placeholder="Search"
              type="search"
              variant="outlined"
              @keydown.enter="search"
            />
          </div>
          <AdvancedSearchCheckboxes />
          <v-expand-transition v-if="currentUser.canAccessAdvisingData">
            <v-card
              v-show="searchStore.includeNotes"
              color="primary"
              variant="outlined"
            >
              <v-card-title>
                <h3 class="notes-and-appointments-filters-header">Filters for notes and appointments</h3>
              </v-card-title>
              <v-card-text class="w-75">
                <div class="px-3">
                  <label class="form-control-label" for="search-option-note-filters-topic">Topic</label>
                  <div>
                    <select
                      id="search-option-note-filters-topic"
                      v-model="topicModel"
                      class="ml-0 my-2 select-menu w-75"
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
                      v-model="searchStore.postedBy"
                      hide-details
                      inline
                    >
                      <v-radio
                        id="search-options-note-filters-posted-by-anyone"
                        :disabled="searchStore.isSearching"
                        :ischecked="searchStore.postedBy === 'anyone'"
                        label="Anyone"
                        value="anyone"
                      />
                      <v-radio
                        id="search-options-note-filters-posted-by-you"
                        :disabled="searchStore.isSearching"
                        :ischecked="searchStore.postedBy === 'you'"
                        label="You"
                        value="you"
                        @change="() => searchStore.setAuthor(null)"
                      />
                      <v-radio
                        id="search-options-note-filters-posted-by-your department"
                        :disabled="searchStore.isSearching"
                        :ischecked="searchStore.postedBy === 'yourDepartment'"
                        label="Your Department(s)"
                        value="yourDepartment"
                      />
                    </v-radio-group>
                  </div>
                  <div class="pt-2 w-75">
                    <label class="form-control-label" for="search-options-note-filters-author">Advisor</label>
                    <span id="notes-search-author-input-label" class="sr-only">
                      Select note author from list of suggested advisors.
                    </span>
                    <Autocomplete
                      id="search-options-note-filters-author"
                      v-model="authorModel"
                      class="mt-1"
                      :compact="true"
                      :disabled="searchStore.isSearching || searchStore.postedBy === 'you'"
                      :fetch="findAdvisorsByName"
                      option-label-key="label"
                      option-value-key="uid"
                      :placeholder="searchStore.postedBy === 'you' ? currentUser.name : 'Enter name...'"
                    />
                  </div>
                  <div class="pt-3 w-75">
                    <label class="form-control-label" for="search-options-note-filters-student">
                      Student (name or SID)
                    </label>
                    <span id="notes-search-student-input-label" class="sr-only">
                      Select a student for notes-related search. Expect auto-suggest as you type name or SID.
                    </span>
                    <Autocomplete
                      id="search-options-note-filters-student"
                      v-model="studentModel"
                      :compact="true"
                      :disabled="searchStore.isSearching"
                      :fetch="findStudentsByNameOrSid"
                      input-labelled-by="notes-search-student-input-label"
                      placeholder="Enter name or SID..."
                    />
                  </div>
                  <div class="pt-3">
                    <label id="search-options-date-range-label" class="form-control-label">
                      Date Range
                    </label>
                    <div class="align-center d-flex mt-2">
                      <label
                        id="search-options-from-date-label"
                        class="text-black mr-2"
                        for="search-options-from-date-input"
                      >
                        <span class="sr-only">Date</span>
                        From
                      </label>
                      <AccessibleDateInput
                        aria-describedby="search-options-date-range-label"
                        container-id="advanced-search-modal"
                        :get-value="() => searchStore.fromDate"
                        id-prefix="search-options-from-date"
                        :max-date="searchStore.toDate || new Date()"
                        :set-value="v => searchStore.setFromDate(v)"
                      ></AccessibleDateInput>
                      <label
                        id="search-options-to-date-label"
                        class="mx-2 text-black"
                        for="search-options-to-date-input"
                      >
                        <span class="sr-only">Date</span>
                        to
                      </label>
                      <AccessibleDateInput
                        aria-describedby="search-options-date-range-label"
                        container-id="advanced-search-modal"
                        :get-value="() => searchStore.toDate"
                        id-prefix="search-options-to-date"
                        :max-date="new Date()"
                        :min-date="searchStore.fromDate"
                        :set-value="v => searchStore.setToDate(v)"
                      ></AccessibleDateInput>
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
              v-if="searchStore.includeNotes && searchStore.isDirty"
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
            class="ml-2"
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
import AdvancedSearchCheckboxes from '@/components/search/AdvancedSearchCheckboxes'
import AdvancedSearchModalHeader from '@/components/search/AdvancedSearchModalHeader'
import Autocomplete from '@/components/util/Autocomplete.vue'
import FocusLock from 'vue-focus-lock'
import ProgressButton from '@/components/util/ProgressButton'
import router from '@/router'
import {addToSearchHistory, findAdvisorsByName} from '@/api/search'
import {alertScreenReader, normalizeId, putFocusNextTick, scrollToTop} from '@/lib/utils'
import {computed, ref, watch} from 'vue'
import {DateTime} from 'luxon'
import {findStudentsByNameOrSid} from '@/api/student'
import {isDate, trim} from 'lodash'
import {labelForSearchInput} from '@/lib/search'
import {mdiTune} from '@mdi/js'
import {useContextStore} from '@/stores/context'
import {useSearchStore} from '@/stores/search'

const searchStore = useSearchStore()
const contextStore = useContextStore()
const currentUser = contextStore.currentUser

const counter = ref(0)
const isFocusAdvSearchButton = ref(false)

const allOptionsUnchecked = computed(() => {
  const admits = searchStore.domain && searchStore.domain.includes('admits') && searchStore.includeAdmits
  return !admits && !searchStore.includeCourses && !searchStore.includeNotes && !searchStore.includeStudents
})
const authorModel = computed(() => ({
  get: () => searchStore.postedBy === 'anyone' ? searchStore.author : null,
  set: value => {
    searchStore.setPostedBy('anyone')
    searchStore.setAuthor(value)
  }
}))
const isSearchDisabled = computed(() => {
  return (
    searchStore.isSearching || allOptionsUnchecked.value ||
    (searchInputRequired.value && !trim(searchStore.queryText)) ||
    !validDateRange.value
  )
})
const queryTextModel = computed({get: () => searchStore.queryText, set: v => searchStore.setQueryText(v)})
const searchInputRequired = computed(() => {
  return !searchStore.includeNotes || !(searchStore.author || searchStore.fromDate || searchStore.toDate || searchStore.postedBy !== 'anyone' || searchStore.student || searchStore.topic)
})
const showAdvancedSearchModel = computed({get: () => !!searchStore.showAdvancedSearch, set: v => searchStore.setShowAdvancedSearch(v)})
const studentModel = computed({get: () => searchStore.student, set: v => searchStore.setStudent(v)})
const topicModel = computed({get: () => searchStore.topic, set: v => searchStore.setTopic(v)})
const validDateRange = computed(() => {
  if (isDate(searchStore.fromDate) && isDate(searchStore.toDate) && (searchStore.toDate < searchStore.fromDate)) {
    return false
  } else if ((searchStore.fromDate && !isDate(searchStore.fromDate)) || (searchStore.toDate && !isDate(searchStore.toDate))) {
    return false
  } else {
    return true
  }
})

watch(() => searchStore.showAdvancedSearch, value => {
  if (value) {
    putFocusNextTick('advanced-search-close')
  } else {
    searchStore.resetAutocompleteInput()
    alertScreenReader('Closed advanced search')
    putFocusNextTick('search-options-panel-toggle')
  }
})

const cancel = () => {
  searchStore.setShowAdvancedSearch(false)
  searchStore.resetAutocompleteInput()
  setTimeout(() => reset(true), 100)
}

const openAdvancedSearch = () => {
  searchStore.setShowAdvancedSearch(true)
  alertScreenReader('Advanced search is open')
}

const reset = force => {
  if (force || !window.location.pathname.startsWith('/search')) {
    searchStore.setQueryText('')
    searchStore.resetAdvancedSearch()
  }
}

const search = () => {
  const q = trim(searchStore.queryText)
  if (q || !searchInputRequired.value) {
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
.form-control-label {
  color: black;
  font-size: 16px;
  font-weight: bold;
}
.notes-and-appointments-filters-header {
  color: #337ab7;
  font-size: 18px;
  font-weight: bolder;
}
</style>
