<template>
  <div>
    <label class="sr-only" for="search-students-input" role="heading">Search for students</label>
    <b-btn
      id="search-options-panel-toggle"
      aria-controls="search-options-panel"
      class="search-options-panel-toggle"
      variant="link"
      @click="showAdvancedSearch"
    >
      Advanced options
    </b-btn>
    <b-modal
      v-model="showAdvancedSearchModal"
      centered
      hide-footer
      hide-header
      size="lg"
      @hidden="cancel"
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
        <div id="search-auto-complete-in-modal" class="mb-3 ml-2 mr-5">
          <span id="search-input-label" class="sr-only">
            Search for students, courses, or notes.
            {{ searchInputRequired ? 'Input is required.' : '' }}
            {{ searchHistory.length ? 'Expect auto-suggest of previous searches.' : '' }}
            (Type / to put focus in the search input field.)
          </span>
          <Autocomplete
            id="advanced-search-students-input"
            aria-labelledby="search-input-label"
            :aria-required="searchInputRequired"
            :base-class="validDateRange === false ? 'disabled' : 'autocomplete'"
            :default-value="input"
            :disabled="validDateRange === false"
            name="q"
            placeholder="Search"
            :search="onChangeAutocomplete"
            type="search"
            @keypress.enter.prevent="$_.noop"
            @submit="onSubmitAutocomplete"
          >
            <template #result="{result, props}">
              <li v-bind="props" :id="`search-auto-suggest-${props['data-result-index']}`">
                <span class="font-size-18">{{ result }}</span>
              </li>
            </template>
          </Autocomplete>
        </div>
        <div class="pt-2">
          <AdvancedSearchCheckboxes class="mb-2 ml-2" />
          <div v-if="$currentUser.canAccessAdvisingData" class="ml-2">
            <b-form-group label="Topic">
              <b-form-select
                id="search-option-note-filters-topic"
                v-model="noteFilters.topic"
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
                <div class="d-flex">
                  <div class="mr-2">
                    <b-form-radio
                      id="search-options-note-filters-posted-by-anyone"
                      v-model="noteFilters.postedBy"
                      :ischecked="noteFilters.postedBy === 'anyone'"
                      name="note-filters-posted-by"
                      value="anyone"
                      @change.native="clearAuthorFilter"
                    >
                      Anyone
                    </b-form-radio>
                  </div>
                  <div>
                    <b-form-radio
                      id="search-options-note-filters-posted-by-you"
                      v-model="noteFilters.postedBy"
                      :ischecked="noteFilters.postedBy === 'you'"
                      name="note-filters-posted-by"
                      value="you"
                      @change.native="clearAuthorFilter"
                    >
                      You
                    </b-form-radio>
                  </div>
                </div>
              </b-form-group>
            </div>
            <div class="pt-2">
              <b-form-group class="w-50" label="Advisor">
                <span id="notes-search-author-input-label" class="sr-only">Select note author from list of suggested advisors.</span>
                <InputTextAutocomplete
                  id="search-options-note-filters-author"
                  v-model="noteAuthor"
                  :disabled="noteFilters.postedBy === 'you'"
                  input-labelled-by="notes-search-author-input-label"
                  :placeholder="noteFilters.postedBy === 'you' ? $currentUser.name : 'Enter name...'"
                  :source="findAdvisorsByName"
                />
              </b-form-group>
            </div>
            <div class="pt-2">
              <b-form-group class="w-50" label="Student (name or SID)">
                <span id="notes-search-student-input-label" class="sr-only">Select a student for notes-related search. Expect auto-suggest as you type name or SID.</span>
                <InputTextAutocomplete
                  id="search-options-note-filters-student"
                  v-model="noteFilters.student"
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
                      v-model="noteFilters.dateFrom"
                      :max-date="noteFilters.dateTo || new Date()"
                      popover-visibility="focus"
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
                      :disabled="!noteFilters.dateFrom"
                      variant="link"
                      @click="noteFilters.dateFrom = null"
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
                      v-model="noteFilters.dateTo"
                      :max-date="new Date()"
                      :min-date="noteFilters.dateFrom || new Date('01/01/1900')"
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
                      :disabled="!noteFilters.dateTo"
                      variant="link"
                      @click="noteFilters.dateTo = null"
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
        </div>
        <div class="mb-2 w-100">
          <div class="justify-content-end d-flex">
            <div class="pr-2">
              <b-btn
                id="advanced-search"
                class="btn-primary-color-override"
                :disabled="allOptionsUnchecked"
                variant="primary"
                @click.prevent="() => search(input)"
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
  </div>
</template>

<script>
import AdvancedSearchCheckboxes from '@/components/search/AdvancedSearchCheckboxes'
import Autocomplete from '@trevoreyre/autocomplete-vue'
import Context from '@/mixins/Context'
import InputTextAutocomplete from '@/components/util/InputTextAutocomplete'
import Scrollable from '@/mixins/Scrollable'
import Search from '@/mixins/Search'
import Util from '@/mixins/Util'
import {addToSearchHistory, findAdvisorsByName} from '@/api/search'
import {findStudentsByNameOrSid} from '@/api/student'

const DEFAULT_NOTE_FILTERS = {
  author: null,
  dateFrom: null,
  dateTo: null,
  postedBy: 'anyone',
  student: null,
  topic: null,
}
export default {
  name: 'AdvancedSearch',
  components: {
    AdvancedSearchCheckboxes,
    Autocomplete,
    InputTextAutocomplete
  },
  mixins: [Context, Scrollable, Search, Util],
  props: {
    onCancel: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    noteFilters: undefined,
    searchHistory: [],
    showAdvancedSearchModal: false
  }),
  computed: {
    allOptionsUnchecked() {
      const admits = this.domain.includes('admits') && this.includeAdmits
      return !admits && !this.includeCourses && !this.includeNotes && !this.includeStudents
    },
    input: {
      get() {
        return this.queryText
      },
      set(value) {
        this.setQueryText(value)
      }
    },
    noteAuthor: {
      get: function() {
        if (this.noteFilters && this.noteFilters.postedBy === 'anyone') {
          return this.noteFilters.author
        } else {
          return null
        }
      },
      set: function(newValue) {
        this.noteFilters.postedBy = 'anyone'
        this.noteFilters.author = newValue
      }
    },
    searchInputRequired() {
      return !(this.includeNotes && (
        this.noteFilters.author ||
        this.noteFilters.dateFrom ||
        this.noteFilters.dateTo ||
        this.noteFilters.postedBy !== 'anyone' ||
        this.noteFilters.student ||
        this.noteFilters.topic
      ))
    },
    validDateRange() {
      if (!this.noteFilters.dateFrom || !this.noteFilters.dateTo) {
        return null
      } else if (this.noteFilters.dateTo < this.noteFilters.dateFrom) {
        return false
      } else {
        return null
      }
    }
  },
  watch: {
    includeAdmits(value) {
      this.$announcer.polite(`Search ${value ? 'will' : 'will not'} include admits.`)
    },
    includeCourses(value) {
      this.$announcer.polite(`Search ${value ? 'will' : 'will not'} include courses.`)
    },
    includeNotes(value) {
      if (value) {
        this.$announcer.polite('Search will include notes and appointments.')
      } else {
        this.$announcer.polite('Search will include neither notes nor appointments.')
      }
    },
    includeStudents(value) {
      this.$announcer.polite(`Search ${value ? 'will' : 'will not'} include students.`)
    }
  },
  created() {
    this.resetNoteFilters()
    this.init().then(this.$_.noop)
  },
  methods: {
    cancel() {
      this.showAdvancedSearchModal = false
      this.noteFilters = DEFAULT_NOTE_FILTERS
      this.resetAdvancedSearch()
      this.onCancel()
    },
    clearAuthorFilter() {
      this.noteFilters.author = null
    },
    dateString(d, format) {
      return this.$options.filters.moment(d, format)
    },
    findAdvisorsByName,
    findStudentsByNameOrSid,
    onChangeAutocomplete(input) {
      this.input = input
      const q = this.$_.trim(input && input.toLowerCase())
      return q.length ? this.searchHistory.filter(s => s.toLowerCase().startsWith(q)) : this.searchHistory
    },
    onSubmitAutocomplete(value) {
      const query = this.$_.trim(value || this.input)
      if (query.length) {
        let el = document.getElementById('search-students-input')
        this.search(el && el.value)
      }
    },
    resetNoteFilters() {
      this.noteFilters = this.$_.clone(DEFAULT_NOTE_FILTERS)
    },
    search(queryText) {
      const q = this.$_.trim(queryText)
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
          if (this.noteFilters.postedBy === 'you') {
            query.advisorCsid = this.$currentUser.csid
          } else if (this.noteFilters.author) {
            query.advisorCsid = this.noteFilters.author.sid
            query.advisorUid = this.noteFilters.author.uid
          }
          if (this.noteFilters.student) {
            query.studentCsid = this.noteFilters.student.sid
          }
          if (this.noteFilters.topic) {
            query.noteTopic = this.noteFilters.topic
          }
          if (this.noteFilters.dateFrom) {
            query.noteDateFrom = this.dateString(this.noteFilters.dateFrom, 'YYYY-MM-DD')
          }
          if (this.noteFilters.dateTo) {
            query.noteDateTo = this.dateString(this.noteFilters.dateTo, 'YYYY-MM-DD')
          }
        }
        this.$router.push(
          {
            path: '/search',
            query: query
          },
          () => {
            this.showAdvancedSearchModal = false
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
    showAdvancedSearch() {
      this.showAdvancedSearchModal = true
      this.$announcer.polite('Advanced search is open')
    }
  }
}
</script>

<style>
#advanced-search-students-input {
  border:  2px solid #337ab7;
  height: 64px;
}
</style>

<style scoped>
.search-options-panel-toggle {
  color: #8bbdda;
  font-size: 12px;
}
.search-panel-feedback {
  color: #fff;
}
</style>
