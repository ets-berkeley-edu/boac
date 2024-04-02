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
      <v-card-title class="pb-0 ml-2">
        <AdvancedSearchModalHeader :on-click-close="cancel" />
      </v-card-title>
      <v-card-text class="pt-1">
        <div class="mb-4">
          <label for="advanced-search-students-input" class="sr-only">{{ labelForSearchInput }}</label>
          <v-combobox
            id="advanced-search-students-input"
            :key="autocompleteInputResetKey"
            v-model="queryText"
            :aria-required="searchInputRequired"
            clearable
            :disabled="isSearching || validDateRange === false"
            hide-details
            hide-no-data
            :items="useSearchStore().searchHistory"
            :menu-icon="null"
            placeholder="Search"
            type="search"
            variant="outlined"
            @keydown.enter.prevent="search"
          />
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
                  <v-radio-group v-model="postedBy" hide-details inline>
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
                <div class="mt-2 w-75">
                  <label class="form-control-label" for="search-options-note-filters-author">Advisor</label>
                  <span id="notes-search-author-input-label" class="sr-only">Select note author from list of suggested advisors.</span>
                  <Autocomplete
                    id="search-options-note-filters-author"
                    v-model="author"
                    class="mt-1"
                    :compact="true"
                    :disabled="isSearching || postedBy === 'you'"
                    :fetch="findAdvisorsByName"
                    option-label-key="label"
                    option-value-key="uid"
                    :placeholder="postedBy === 'you' ? currentUser.name : 'Enter name...'"
                  />
                </div>
                <div class="mt-3 w-75">
                  <label class="form-control-label" for="search-options-note-filters-student">Student (name or SID)</label>
                  <span id="notes-search-student-input-label" class="sr-only">Select a student for notes-related search. Expect auto-suggest as you type name or SID.</span>
                  <Autocomplete
                    id="search-options-note-filters-student"
                    v-model="student"
                    :compact="true"
                    :disabled="isSearching"
                    :fetch="findStudentsByNameOrSid"
                    input-labelled-by="notes-search-student-input-label"
                    placeholder="Enter name or SID..."
                  />
                </div>
                <div class="mt-3">
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
                    <VCDatePicker v-model="fromDate" :input-debounce="500">
                      <template #default="{inputValue, inputEvents}">
                        <v-text-field
                          id="search-options-note-filters-last-updated-from"
                          :value="inputValue"
                          v-on="inputEvents"
                        />
                      </template>
                    </VCDatePicker>
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
                    <VCDatePicker v-model="toDate" :input-debounce="500">
                      <template #default="{inputValue, inputEvents}">
                        <VCBaseInput
                          id="search-options-note-filters-last-updated-to"
                          :value="inputValue"
                          v-on="inputEvents"
                        />
                      </template>
                    </VCDatePicker>
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
              </div>
            </v-card-actions>
          </v-card>
        </v-expand-transition>
        <div class="align-center d-flex my-2 pr-2">
          <div v-if="includeNotes && isDirty" class="flex-grow-1">
            <v-btn
              id="reset-advanced-search-form-btn"
              :disabled="isSearching"
              text="Reset"
              variant="text"
              @click="() => reset(true)"
            />
          </div>
          <v-btn
            id="advanced-search"
            class="btn-primary-color-override"
            color="primary"
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
            variant="text"
            @click="cancel"
          />
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import AdvancedSearchCheckboxes from '@/components/search/AdvancedSearchCheckboxes'
import AdvancedSearchModalHeader from '@/components/search/AdvancedSearchModalHeader'
import Autocomplete from '@/components/util/Autocomplete.vue'
import {findStudentsByNameOrSid} from '@/api/student'
import {mdiClose, mdiTune} from '@mdi/js'
import {useSearchStore} from '@/stores/search'
</script>

<script>
import Context from '@/mixins/Context'
import SearchSession from '@/mixins/SearchSession'
import Util from '@/mixins/Util'
import {addToSearchHistory, findAdvisorsByName} from '@/api/search'
import {scrollToTop} from '@/lib/utils'
import {DateTime} from 'luxon'

export default {
  name: 'AdvancedSearchModal',
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
    // onChangeAutocomplete(input) {
    //   this.queryText = input
    //   const q = this._trim(input && input.toLowerCase())
    //   return q.length ? this.searchHistory.filter(s => s.toLowerCase().startsWith(q)) : this.searchHistory
    // },
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
    }
  }
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
.z-index-0 {
  z-index: 0;
}
</style>
