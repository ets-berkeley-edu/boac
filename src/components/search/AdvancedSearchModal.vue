<template>
  <v-tooltip location="bottom" text="Advanced search options">
    <template #activator="{props}">
      <v-btn
        id="search-options-panel-toggle"
        v-bind="props"
        class="px-0"
        :class="{'border-0': !isFocusAdvSearchButton}"
        color="white"
        icon
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
  <v-dialog v-model="showAdvancedSearch">
    <v-card max-width="800">
      <v-card-title>
        <div class="align-center d-flex justify-space-between">
          <h2
            id="advanced-search-header"
            class="font-size-24 font-weight-700"
            tabindex="-1"
          >
            Advanced Search
          </h2>
          <div class="faint-text">
            <v-btn
              id="advanced-search-close"
              class="font-size-14 font-weight-700"
              elevation="0"
              icon
              @click="cancel"
              @keydown.enter="cancel"
            >
              <span class="sr-only">Close</span>
              <v-icon
                color="primary"
                :icon="mdiClose"
                size="medium"
              />
            </v-btn>
          </div>
        </div>
      </v-card-title>
      <v-card-text>
        <div>
          <div>
            <label id="search-input-label" class="sr-only">{{ labelForSearchInput }}</label>
            <!--
            TODO:
            <Autocomplete
              id="advanced-search-students-input"
              :key="autocompleteInputResetKey"
              aria-labelledby="search-input-label"
              :aria-required="searchInputRequired"
              :base-class="validDateRange === false ? 'disabled' : 'autocomplete'"
              :default-value="queryText"
              :disabled="isSearching || validDateRange === false"
              name="q"
              placeholder="Search"
              :search="onChangeAutocomplete"
              type="search"
              @keydown.enter.prevent="search"
              @submit="setQueryText"
            >
              <template #result="{result, props}">
                <li v-bind="props" :id="`search-auto-suggest-${props['data-result-index']}`">
                  <span class="font-size-18">{{ result }}</span>
                </li>
              </template>
            </Autocomplete>
            -->
          </div>
          <AdvancedSearchCheckboxes />
          <v-expand-transition v-if="currentUser.canAccessAdvisingData">
            <v-card v-show="includeNotes" variant="outlined" color="primary">
              <v-card-title>
                <h3 class="notes-and-appointments-filters-header">Filters for notes and appointments</h3>
              </v-card-title>
              <v-card-actions>
                <div class="px-3">
                  <label class="form-control-label" for="search-option-note-filters-topic">Topic</label>
                  <div>
                    <v-select
                      id="search-option-note-filters-topic"
                      v-model="topic"
                      base-color="black"
                      bg-color="transparent"
                      class="ml-0 my-2 w-75"
                      color="black"
                      density="compact"
                      :disabled="isSearching"
                      hide-details
                      item-title="text"
                      item-value="value"
                      :items="topicOptions"
                      label="Select..."
                      return-object
                      variant="outlined"
                    >
                      <template #item="{props, item}">
                        <v-list-item v-bind="props">
                          <template #title="{title}">
                            <span
                              :id="`batch-note-${type}-option-${item.value}`"
                              :key="item.value"
                              :aria-label="`Add ${type} ${title}`"
                            >
                              {{ title }}
                            </span>
                          </template>
                        </v-list-item>
                      </template>
                    </v-select>
                  </div>
                  <div class="mt-4">
                    <label class="form-control-label">Posted By</label>
                    <v-radio-group v-model="postedBy" inline>
                      <v-radio
                        id="search-options-note-filters-posted-by-anyone"
                        :ischecked="postedBy === 'anyone'"
                        :disabled="isSearching"
                        label="Anyone"
                        value="anyone"
                      />
                      <v-radio
                        id="search-options-note-filters-posted-by-you"
                        :ischecked="postedBy === 'you'"
                        :disabled="isSearching"
                        label="You"
                        value="you"
                        @change="() => setAuthor(null)"
                      />
                    </v-radio-group>
                  </div>
                  <label class="form-control-label" for="search-options-note-filters-author">Advisor</label>
                  <span id="notes-search-author-input-label" class="sr-only">Select note author from list of suggested advisors.</span>
                  <InputTextAutocomplete
                    id="search-options-note-filters-author"
                    v-model="author"
                    :disabled="isSearching || postedBy === 'you'"
                    input-labelled-by="notes-search-author-input-label"
                    :placeholder="postedBy === 'you' ? currentUser.name : 'Enter name...'"
                    :source="findAdvisorsByName"
                  />
                  <label class="form-control-label" for="search-options-note-filters-student">Student (name or SID)</label>
                  <span id="notes-search-student-input-label" class="sr-only">Select a student for notes-related search. Expect auto-suggest as you type name or SID.</span>
                  <InputTextAutocomplete
                    id="search-options-note-filters-student"
                    v-model="student"
                    :disabled="isSearching"
                    :demo-mode-blur="true"
                    input-labelled-by="notes-search-student-input-label"
                    placeholder="Enter name or SID..."
                    :source="findStudentsByNameOrSid"
                  />
                  <label class="form-control-label" for="search-options-note-filters-last-updated-from">Date Range</label>
                  <div class="d-flex">
                    <label
                      id="note-filters-date-from-label"
                      class="text-black"
                      for="search-options-note-filters-last-updated-from"
                    >
                      <span class="sr-only">Date</span>
                      From
                    </label>
                    <VDatePicker v-model="fromDate" :input-debounce="500">
                      <template #default="{inputValue, inputEvents}">
                        <VBaseInput
                          id="search-options-note-filters-last-updated-from"
                          :value="inputValue"
                          v-on="inputEvents"
                        />
                      </template>
                    </VDatePicker>
                    <!--
                    <template #default="{inputValue, inputEvents}">
                      <input
                        id="search-options-note-filters-last-updated-from"
                        aria-labelledby="note-filters-date-from-label"
                        class="form-control"
                        :disabled="isSearching"
                        name="note-filters-date-from"
                        placeholder="MM/DD/YYYY"
                        type="text"
                        :value="inputValue"
                        v-on="inputEvents"
                      />
                    </template>
                    -->
                    <div class="sr-only">
                      <v-btn
                        id="search-options-note-filters-last-updated-from-clear"
                        :disabled="!fromDate"
                        icon
                        @click="() => setFromDate(null)"
                      >
                        <span class="sr-only">Clear the 'from' date.</span>
                        <v-icon
                          class="font-size-14"
                          :icon="mdiClose"
                          size="sm"
                        />
                      </v-btn>
                    </div>
                    <label
                      id="note-filters-date-to-label"
                      for="search-options-note-filters-last-updated-to"
                      class="text-black"
                    >
                      <span class="sr-only">Date</span>
                      to
                    </label>
                    <VDatePicker v-model="toDate" :input-debounce="500">
                      <template #default="{inputValue, inputEvents}">
                        <VBaseInput
                          id="search-options-note-filters-last-updated-to"
                          :value="inputValue"
                          v-on="inputEvents"
                        />
                      </template>
                    </VDatePicker>
                    <!--
                      <template #default="{inputValue, inputEvents}">
                        <input
                          id="search-options-note-filters-last-updated-to"
                          aria-labelledby="note-filters-date-to-label"
                          class="form-control"
                          :disabled="isSearching"
                          name="note-filters-date-to"
                          placeholder="MM/DD/YYYY"
                          type="text"
                          :value="inputValue"
                          v-on="inputEvents"
                        />
                      </template>
                    -->
                    <v-btn
                      id="search-options-note-filters-last-updated-to-clear"
                      class="sr-only"
                      :disabled="!toDate"
                      icon
                      @click="toDate = null"
                    >
                      Clear the 'to' date.
                      <v-icon
                        class="font-size-14"
                        :icon="mdiClose"
                        size="sm"
                      />
                    </v-btn>
                  </div>
                </div>
              </v-card-actions>
            </v-card>
          </v-expand-transition>
          <div>
            <v-btn
              v-if="includeNotes && isDirty"
              id="reset-advanced-search-form-btn"
              :disabled="isSearching"
              size="sm"
              @click="() => reset(true)"
            >
              Reset
            </v-btn>
            <v-btn
              id="advanced-search"
              class="btn-primary-color-override"
              :disabled="isSearching || allOptionsUnchecked || (searchInputRequired && !_trim(queryText))"
              @click.prevent="search"
            >
              <span v-if="isSearching" class="px-1">
                <v-progress-circular
                  class="mr-2"
                  indeterminate
                  size="small"
                />
                <span>Searching...</span>
              </span>
              <span v-if="!isSearching">
                Search
              </span>
            </v-btn>
            <v-btn
              id="advanced-search-cancel"
              text="Cancel"
              @click="cancel"
            />
          </div>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import {findStudentsByNameOrSid} from '@/api/student'
import {mdiClose, mdiTune} from '@mdi/js'
</script>

<script>
import AdvancedSearchCheckboxes from '@/components/search/AdvancedSearchCheckboxes'
import Context from '@/mixins/Context'
import InputTextAutocomplete from '@/components/util/InputTextAutocomplete'
import SearchSession from '@/mixins/SearchSession'
import Util from '@/mixins/Util'
import {addToSearchHistory, findAdvisorsByName} from '@/api/search'
import {scrollToTop} from '@/lib/utils'
import {DateTime} from 'luxon'

export default {
  name: 'AdvancedSearchModal',
  components: {
    AdvancedSearchCheckboxes,
    InputTextAutocomplete
  },
  mixins: [Context, SearchSession, Util],
  data: () => ({
    isFocusAdvSearchButton: false,
    counter: 0
  }),
  computed: {
    allOptionsUnchecked() {
      const admits = this.domain && this.domain.includes('admits') && this.includeAdmits
      return !admits && !this.includeCourses && !this.includeNotes && !this.includeStudents
    },
    searchInputRequired() {
      return !this.includeNotes || !(this.author || this.fromDate || this.toDate || this.postedBy !== 'anyone' || this.student || this.topic)
    },
    validDateRange() {
      if (!this.fromDate || !this.toDate) {
        return null
      } else if (this.toDate < this.fromDate) {
        return false
      } else {
        return null
      }
    }
  },
  watch: {
    showAdvancedSearch(value) {
      if (value) {
        this.putFocusNextTick('advanced-search-header')
      } else {
        this.resetAutocompleteInput()
      }
    }
  },
  methods: {
    cancel() {
      this.showAdvancedSearch = false
      this.resetAutocompleteInput()
      setTimeout(this.reset, 100)
    },
    onChangeAutocomplete(input) {
      this.queryText = input
      const q = this._trim(input && input.toLowerCase())
      return q.length ? this.searchHistory.filter(s => s.toLowerCase().startsWith(q)) : this.searchHistory
    },
    openAdvancedSearch() {
      this.showAdvancedSearch = true
      this.alertScreenReader('Advanced search is open')
    },
    reset(force) {
      if (force || !this.$route.path.startsWith('/search')) {
        this.queryText = ''
        this.resetAdvancedSearch()
      }
    },
    search() {
      const q = this._trim(this.queryText)
      if (q || !this.searchInputRequired) {
        const query = {
          _: this.counter++,
          notes: this.includeNotes,
          students: this.includeStudents
        }
        if (this.includeAdmits) {
          query.admits = this.includeAdmits
        }
        if (this.includeCourses) {
          query.courses = this.includeCourses
        }
        if (q) {
          query.q = q
        }
        if (this.includeNotes) {
          if (this.postedBy === 'you') {
            query.advisorCsid = this.currentUser.csid
          } else if (this.author) {
            query.advisorCsid = this.author.sid
            query.advisorUid = this.author.uid
          }
          if (this.student) {
            query.studentCsid = this.student.sid
          }
          if (this.topic) {
            query.noteTopic = this.topic
          }
          if (this.fromDate) {
            query.noteDateFrom = DateTime.fromJSDate(this.fromDate).toFormat('YYYY-MM-DD')
          }
          if (this.toDate) {
            query.noteDateTo = DateTime.fromJSDate(this.toDate).toFormat('YYYY-MM-DD')

          }
        }
        this.$router.push(
          {
            path: '/search',
            query: query
          },
          () => {
            this.showAdvancedSearch = false
          }
        )
        if (q) {
          addToSearchHistory(q).then(history => {
            this.searchHistory = history
          })
        }
      } else {
        this.alertScreenReader('Search input is required')
        this.putFocusNextTick('search-students-input')
      }
      scrollToTop()
    },
    setQueryText(value) {
      this.queryText = value
    }
  }
}
</script>

<style>
#advanced-search-students-input {
  border:  1px solid #337ab7;
  height: 64px;
}
</style>

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
.z-index-0 {
  z-index: 0;
}
</style>
