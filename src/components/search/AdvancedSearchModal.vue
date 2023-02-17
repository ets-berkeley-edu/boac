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
          <h2 class="font-size-24 font-weight-700">Advanced Search</h2>
        </div>
        <div class="faint-text mr-1">
          <b-btn variant="link">
            <span class="sr-only">Close</span>
            <b-btn
              id="advanced-search-close"
              class="pt-0"
              variant="link"
              @click="cancel"
            >
              <span class="sr-only">Cancel</span>
              <font-awesome class="font-size-14" icon="times" />
            </b-btn>
          </b-btn>
        </div>
      </div>
      <div class="mb-3 ml-2 mr-5">
        <span id="search-input-label" class="sr-only">
          Search for students, courses, or notes.
          {{ searchInputRequired ? 'Input is required.' : '' }}
          {{ searchHistory.length ? 'Expect auto-suggest of previous searches.' : '' }}
          (Type / to put focus in the search input field.)
        </span>
        <Autocomplete
          id="advanced-search-students-input"
          :key="autocompleteInputResetKey"
          aria-labelledby="search-input-label"
          :aria-required="searchInputRequired"
          :base-class="validDateRange === false ? 'disabled' : 'autocomplete'"
          :default-value="queryText"
          :disabled="validDateRange === false"
          name="q"
          placeholder="Search"
          :search="onChangeAutocomplete"
          type="search"
          @keydown.enter="search"
          @submit="onSubmitAutocomplete"
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
          v-if="$currentUser.canAccessAdvisingData && includeNotes"
          :aria-expanded="includeNotes"
          class="ml-2"
        >
          <b-form-group label="Topic">
            <b-form-select
              id="search-option-note-filters-topic"
              v-model="topic"
              class="w-75"
              size="md"
              :options="topicOptions"
            >
              <template v-slot:first>
                <option :value="null">Any topic</option>
              </template>
            </b-form-select>
          </b-form-group>
          <div class="pt-2">
            <b-form-group label="Posted By">
              <b-form-radio-group v-model="postedBy">
                <div class="d-flex">
                  <div class="mr-2">
                    <b-form-radio
                      id="search-options-note-filters-posted-by-anyone"
                      class="z-index-0"
                      :ischecked="postedBy === 'anyone'"
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
          <div class="pt-2">
            <b-form-group class="w-50" label="Advisor">
              <span id="notes-search-author-input-label" class="sr-only">Select note author from list of suggested advisors.</span>
              <InputTextAutocomplete
                id="search-options-note-filters-author"
                v-model="author"
                :disabled="postedBy === 'you'"
                input-labelled-by="notes-search-author-input-label"
                :placeholder="postedBy === 'you' ? $currentUser.name : 'Enter name...'"
                :source="findAdvisorsByName"
              />
            </b-form-group>
          </div>
          <div class="pt-2">
            <b-form-group class="w-50" label="Student (name or SID)">
              <span id="notes-search-student-input-label" class="sr-only">Select a student for notes-related search. Expect auto-suggest as you type name or SID.</span>
              <InputTextAutocomplete
                id="search-options-note-filters-student"
                v-model="student"
                :demo-mode-blur="true"
                input-labelled-by="notes-search-student-input-label"
                placeholder="Enter name or SID..."
                :source="findStudentsByNameOrSid"
              />
            </b-form-group>
          </div>
          <div class="pt-2">
            <b-form-group label="Date Range">
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
                    id="search-options-note-filters-last-updated-from-clear"
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
      <div class="mb-2 w-100">
        <div class="align-items-center d-flex">
          <div v-if="includeNotes" class="flex-grow-1">
            <b-btn
              v-if="queryText || author || fromDate || toDate || postedBy !== 'anyone' || student || topic"
              id="reset-advanced-search-form-btn"
              size="sm"
              variant="link"
              @click="reset"
            >
              Reset
            </b-btn>
          </div>
          <div class="pr-2">
            <b-btn
              id="advanced-search"
              class="btn-primary-color-override"
              :disabled="allOptionsUnchecked || (searchInputRequired && !queryText)"
              variant="primary"
              @click.prevent="search"
            >
              Search
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
    searchHistory: []
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
  methods: {
    cancel() {
      this.onHidden()
      setTimeout(this.resetAdvancedSearch, 100)
    },
    findAdvisorsByName,
    findStudentsByNameOrSid,
    onChangeAutocomplete(input) {
      this.queryText = input
      const q = this.$_.trim(input && input.toLowerCase())
      return q.length ? this.searchHistory.filter(s => s.toLowerCase().startsWith(q)) : this.searchHistory
    },
    onHidden() {
      this.showAdvancedSearch = false
      this.resetAutocompleteInput()
    },
    onSubmitAutocomplete(value) {
      const query = this.$_.trim(value || this.queryText)
      if (query.length) {
        const el = document.getElementById('search-students-input')
        this.queryText = el && el.value
        this.search()
      }
    },
    reset() {
      this.queryText = ''
      this.resetAdvancedSearch()
    },
    search() {
      const q = this.$_.trim(this.queryText)
      if (q || !this.searchInputRequired) {
        const query = {
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
            query.advisorCsid = this.$currentUser.csid
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
.z-index-0 {
  z-index: 0;
}
</style>
