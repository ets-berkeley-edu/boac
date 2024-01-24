<template>
  <b-modal
    v-model="showAdvancedSearch"
    centered
    hide-footer
    hide-header
    size="lg"
    @hidden="onHidden"
  >
    <div>
      <div class="align-items-center d-flex justify-content-between my-2">
        <div class="ml-2">
          <h2
            id="advanced-search-header"
            class="font-size-24 font-weight-700"
            tabindex="-1"
          >
            Advanced Search
          </h2>
        </div>
        <div class="faint-text mr-1">
          <b-btn
            id="advanced-search-close"
            class="pt-0"
            variant="link"
            @click="cancel"
            @keydown.enter="cancel"
          >
            <span class="sr-only">Close</span>
            <font-awesome class="font-size-14" icon="times" />
          </b-btn>
        </div>
      </div>
      <div class="mb-3 mx-2">
        <label id="search-input-label" class="sr-only">{{ labelForSearchInput }}</label>
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
      </div>
      <AdvancedSearchCheckboxes class="mb-2 ml-2" />
      <transition class="pt-2" name="drawer">
        <div
          v-if="currentUser.canAccessAdvisingData && includeNotes"
          class="border border-info mb-3 mx-2 p-3 rounded"
        >
          <h3 class="notes-and-appointments-filters-header">Filters for notes and appointments</h3>
          <label class="font-size-16 font-weight-700" for="search-option-note-filters-topic">Topic</label>
          <div>
            <b-form-select
              id="search-option-note-filters-topic"
              v-model="topic"
              class="w-75"
              :disabled="isSearching"
              size="md"
              :options="topicOptions"
            >
              <template v-slot:first>
                <option :value="null">Any topic</option>
              </template>
            </b-form-select>
          </div>
          <div class="pt-3">
            <b-form-group class="mb-0" label="Posted By">
              <b-form-radio-group v-model="postedBy">
                <div class="d-flex">
                  <div class="mr-2">
                    <b-form-radio
                      id="search-options-note-filters-posted-by-anyone"
                      class="z-index-0"
                      :ischecked="postedBy === 'anyone'"
                      :disabled="isSearching"
                      name="note-filters-posted-by"
                      value="anyone"
                    >
                      Anyone
                    </b-form-radio>
                  </div>
                  <div>
                    <b-form-radio
                      id="search-options-note-filters-posted-by-you"
                      class="z-index-0"
                      :ischecked="postedBy === 'you'"
                      :disabled="isSearching"
                      name="note-filters-posted-by"
                      value="you"
                      @change.native="() => setAuthor(null)"
                    >
                      You
                    </b-form-radio>
                  </div>
                </div>
              </b-form-radio-group>
            </b-form-group>
          </div>
          <div class="pt-3">
            <b-form-group class="mb-0 w-50" label="Advisor">
              <span id="notes-search-author-input-label" class="sr-only">Select note author from list of suggested advisors.</span>
              <InputTextAutocomplete
                id="search-options-note-filters-author"
                v-model="author"
                :disabled="isSearching || postedBy === 'you'"
                input-labelled-by="notes-search-author-input-label"
                :placeholder="postedBy === 'you' ? currentUser.name : 'Enter name...'"
                :source="findAdvisorsByName"
              />
            </b-form-group>
          </div>
          <div class="pt-3">
            <b-form-group class="mb-0 w-50" label="Student (name or SID)">
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
            </b-form-group>
          </div>
          <div class="pt-3">
            <b-form-group class="mb-0" label="Date Range">
              <div class="align-items-center d-flex">
                <div>
                  <label
                    id="note-filters-date-from-label"
                    for="search-options-note-filters-last-updated-from"
                    class="font-weight-500 pt-1 px-2"
                  >
                    <span class="sr-only">Date</span>
                    From
                  </label>
                </div>
                <div>
                  <v-date-picker
                    :max-date="toDate || new Date()"
                    popover-visibility="focus"
                    :value="fromDate"
                    @input="v => setFromDate(v)"
                  >
                    <template v-slot="{inputValue, inputEvents}">
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
                  </v-date-picker>
                </div>
                <div class="sr-only">
                  <b-btn
                    id="search-options-note-filters-last-updated-from-clear"
                    :disabled="!fromDate"
                    variant="link"
                    @click="() => setFromDate(null)"
                  >
                    <span class="sr-only">Clear the 'from' date.</span>
                    <font-awesome
                      class="font-size-14"
                      icon="times"
                      size="sm"
                    />
                  </b-btn>
                </div>
                <div>
                  <label
                    id="note-filters-date-to-label"
                    for="search-options-note-filters-last-updated-to"
                    class="font-weight-500 pt-1 px-2"
                  >
                    <span class="sr-only">Date</span>
                    to
                  </label>
                </div>
                <div>
                  <v-date-picker
                    v-model="toDate"
                    :max-date="new Date()"
                    :min-date="fromDate || new Date('01/01/1900')"
                    popover-visibility="focus"
                  >
                    <template v-slot="{inputValue, inputEvents}">
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
                  </v-date-picker>
                </div>
                <div class="sr-only">
                  <b-btn
                    id="search-options-note-filters-last-updated-to-clear"
                    :disabled="!toDate"
                    variant="link"
                    @click="toDate = null"
                  >
                    <span class="sr-only">Clear the 'to' date.</span>
                    <font-awesome
                      class="font-size-14"
                      icon="times"
                      size="sm"
                    />
                  </b-btn>
                </div>
              </div>
            </b-form-group>
          </div>
        </div>
      </transition>
      <div class="my-2 pr-2">
        <div class="align-items-center d-flex">
          <div v-if="includeNotes" class="flex-grow-1">
            <b-btn
              v-if="isDirty"
              id="reset-advanced-search-form-btn"
              :disabled="isSearching"
              size="sm"
              variant="link"
              @click="() => reset(true)"
            >
              Reset
            </b-btn>
          </div>
          <div class="pr-2">
            <b-btn
              id="advanced-search"
              class="btn-primary-color-override"
              :disabled="isSearching || allOptionsUnchecked || (searchInputRequired && !_trim(queryText))"
              variant="primary"
              @click.prevent="search"
            >
              <span v-if="isSearching" class="px-1">
                <b-spinner small class="mr-2"></b-spinner>
                <span>Searching...</span>
              </span>
              <span v-if="!isSearching">
                Search
              </span>
            </b-btn>
          </div>
          <div>
            <b-btn
              id="advanced-search-cancel"
              class="pl-2"
              variant="link"
              @click="cancel"
            >
              Cancel
            </b-btn>
          </div>
        </div>
      </div>
    </div>
  </b-modal>
</template>

<script>
import AdvancedSearchCheckboxes from '@/components/search/AdvancedSearchCheckboxes'
import Autocomplete from '@trevoreyre/autocomplete-vue'
import Context from '@/mixins/Context'
import InputTextAutocomplete from '@/components/util/InputTextAutocomplete'
import Scrollable from '@/mixins/Scrollable'
import SearchSession from '@/mixins/SearchSession'
import Util from '@/mixins/Util'
import {addToSearchHistory, findAdvisorsByName} from '@/api/search'
import {findStudentsByNameOrSid} from '@/api/student'

export default {
  name: 'AdvancedSearchModal',
  components: {
    AdvancedSearchCheckboxes,
    Autocomplete,
    InputTextAutocomplete
  },
  mixins: [Context, Scrollable, SearchSession, Util],
  data: () => ({
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
        this.$putFocusNextTick('advanced-search-header')
      }
    }
  },
  methods: {
    cancel() {
      this.onHidden()
      setTimeout(this.reset, 100)
    },
    findAdvisorsByName,
    findStudentsByNameOrSid,
    onChangeAutocomplete(input) {
      this.queryText = input
      const q = this._trim(input && input.toLowerCase())
      return q.length ? this.searchHistory.filter(s => s.toLowerCase().startsWith(q)) : this.searchHistory
    },
    onHidden() {
      this.showAdvancedSearch = false
      this.resetAutocompleteInput()
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
            query.noteDateFrom = this.$options.filters.moment(this.fromDate, 'YYYY-MM-DD')
          }
          if (this.toDate) {
            query.noteDateTo = this.$options.filters.moment(this.toDate, 'YYYY-MM-DD')
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
        this.$announcer.polite('Search input is required')
        this.$putFocusNextTick('search-students-input')
      }
      this.scrollToTop()
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
.notes-and-appointments-filters-header {
  color: #337ab7;
  font-size: 18px;
  font-weight: bolder;
}
.z-index-0 {
  z-index: 0;
}
</style>
