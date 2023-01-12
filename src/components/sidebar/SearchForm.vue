<template>
  <div v-hotkey="{'/': () => $putFocusNextTick('search-students-input')}">
    <label class="sr-only" for="search-students-form" role="heading">Search Form</label>
    <form class="mb-3 mt-2 mx-2">
      <div class="align-items-end d-flex flex-wrap font-size-14 text-nowrap text-white">
        <div class="pb-1 pr-1">
          <font-awesome icon="search" />
        </div>
        <div class="pr-1 search-form-label">
          <label class="mb-0" for="search-students-input">Search</label>
        </div>
        <div class="pb-1 search-options-panel-toggle">
          (<b-btn
            id="search-options-panel-toggle"
            aria-controls="search-options-panel"
            class="p-0 search-options-panel-toggle"
            variant="link"
            @click="toggleSearchOptions"
          >
            {{ showSearchOptions ? 'hide' : 'show' }} options
          </b-btn>)
        </div>
      </div>
      <div>
        <b-collapse
          id="search-options-panel"
          v-model="showSearchOptions"
          class="mt-2 text-white"
        >
          <span class="sr-only">
            Search options
          </span>
          <div v-if="domain.includes('admits')" class="d-flex">
            <b-form-checkbox
              id="search-include-admits-checkbox"
              v-model="includeAdmits"
              plain
            >
            </b-form-checkbox>
            <label
              for="search-include-admits-checkbox"
              class="search-form-label"
            >
              <span class="sr-only">Search for</span>
              Admitted Students
            </label>
          </div>
          <div class="d-flex">
            <b-form-checkbox
              id="search-include-students-checkbox"
              v-model="includeStudents"
              plain
            >
            </b-form-checkbox>
            <label
              for="search-include-students-checkbox"
              class="search-form-label"
            >
              <span class="sr-only">Search for</span>
              Students
            </label>
          </div>
          <div v-if="domain.includes('courses')" class="d-flex">
            <b-form-checkbox
              id="search-include-courses-checkbox"
              v-model="includeCourses"
              plain
            >
            </b-form-checkbox>
            <label
              for="search-include-courses-checkbox"
              class="search-form-label"
            >
              <span class="sr-only">Search for</span>
              Classes
            </label>
          </div>
          <div v-if="$currentUser.canAccessAdvisingData" class="d-flex flex-wrap">
            <b-form-checkbox
              id="search-include-notes-checkbox"
              v-model="includeNotes"
              plain
            >
            </b-form-checkbox>
            <label
              for="search-include-notes-checkbox"
              class="search-form-label"
            >
              <span class="sr-only">Search for</span>
              Notes &amp; Appointments
            </label>
            <transition name="drawer">
              <div v-if="includeNotes">
                <b-btn
                  id="search-options-note-filters-toggle"
                  aria-controls="search-options-note-filters-subpanel"
                  :aria-expanded="showNoteFilters"
                  class="pl-0 pt-0 search-options-panel-toggle text-nowrap"
                  variant="link"
                  @click="toggleNoteFilters"
                >
                  ({{ showNoteFilters ? 'hide' : 'show' }} <span class="sr-only">note and appointment </span>search filters)
                </b-btn>
              </div>
            </transition>
          </div>
          <b-collapse
            v-if="$currentUser.canAccessAdvisingData"
            id="search-options-note-filters-subpanel"
            v-model="showNoteFilters"
            class="ml-1 text-white"
          >
            <b-form-group label="Topic" label-for="search-option-note-filters-topic">
              <b-form-select
                id="search-option-note-filters-topic"
                v-model="noteFilters.topic"
                :options="topicOptions"
              >
                <template v-slot:first>
                  <option :value="null">Any topic</option>
                </template>
              </b-form-select>
            </b-form-group>
            <b-form-group label="Posted By">
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
            </b-form-group>
            <b-form-group label="Advisor" label-for="search-options-note-filters-author-input">
              <span id="notes-search-author-input-label" class="sr-only">Select note author from list of suggested advisors.</span>
              <Autocomplete
                id="search-options-note-filters-author"
                v-model="noteAuthor"
                :disabled="noteFilters.postedBy === 'you'"
                input-labelled-by="notes-search-author-input-label"
                :placeholder="noteFilters.postedBy === 'you' ? $currentUser.name : 'Enter name...'"
                :source="findAdvisorsByName"
              />
            </b-form-group>
            <b-form-group label="Student (name or SID)" label-for="search-options-note-filters-student-input">
              <span id="notes-search-student-input-label" class="sr-only">Select a student for notes-related search. Expect auto-suggest as you type name or SID.</span>
              <Autocomplete
                id="search-options-note-filters-student"
                v-model="noteFilters.student"
                :demo-mode-blur="true"
                input-labelled-by="notes-search-student-input-label"
                placeholder="Enter name or SID..."
                :source="findStudentsByNameOrSid"
              />
            </b-form-group>
            <b-form-group label="Date Range">
              <label
                id="note-filters-date-from-label"
                for="search-options-note-filters-last-updated-from"
                class="search-form-label"
              >
                <span class="sr-only">Date</span>
                From
              </label>
              <div class="d-flex">
                <div class="w-100">
                  <v-date-picker
                    v-model="noteFilters.dateFrom"
                    :max-date="noteFilters.dateTo || maxDate"
                    popover-visibility="focus"
                  >
                    <template v-slot="{inputValue, inputEvents}">
                      <input
                        id="search-options-note-filters-last-updated-from"
                        aria-labelledby="note-filters-date-from-label"
                        class="search-input-date form-control"
                        name="note-filters-date-from"
                        placeholder="MM/DD/YYYY"
                        type="text"
                        :value="inputValue"
                        v-on="inputEvents"
                      />
                    </template>
                  </v-date-picker>
                </div>
                <div v-if="noteFilters.dateFrom">
                  <b-btn
                    id="search-options-note-filters-last-updated-from-clear"
                    class="search-input-date"
                    @click="noteFilters.dateFrom = null"
                  >
                    <font-awesome icon="times" />
                    <span class="sr-only">Clear date from</span>
                  </b-btn>
                </div>
              </div>
              <label
                id="note-filters-date-to-label"
                for="search-options-note-filters-last-updated-to"
                class="search-form-label"
              >
                <span class="sr-only">Date</span>
                To
              </label>
              <div class="d-flex">
                <div class="w-100">
                  <v-date-picker
                    v-model="noteFilters.dateTo"
                    :max-date="maxDate"
                    :min-date="noteFilters.dateFrom || minDate"
                    popover-visibility="focus"
                  >
                    <template v-slot="{inputValue, inputEvents}">
                      <input
                        id="search-options-note-filters-last-updated-to"
                        aria-labelledby="note-filters-date-to-label"
                        class="search-input-date form-control"
                        name="note-filters-date-to"
                        placeholder="MM/DD/YYYY"
                        type="text"
                        :value="inputValue"
                        v-on="inputEvents"
                      />
                    </template>
                  </v-date-picker>
                </div>
                <div v-if="noteFilters.dateTo">
                  <b-btn
                    id="search-options-note-filters-last-updated-to-clear"
                    class="search-input-date"
                    @click="noteFilters.dateTo = null"
                  >
                    <font-awesome icon="times"></font-awesome>
                    <span class="sr-only">Clear date to</span>
                  </b-btn>
                </div>
              </div>
              <b-form-invalid-feedback :state="validDateRange" class="search-panel-feedback">
                <font-awesome icon="exclamation-triangle" class="text-warning pr-1" />
                <span aria-live="polite" role="alert">
                  "To" must be later than or equal to "From."
                </span>
              </b-form-invalid-feedback>
            </b-form-group>
          </b-collapse>
        </b-collapse>
      </div>
      <span
        v-if="showUncheckedOptionsAlert"
        class="sr-only"
        aria-live="polite"
        role="alert"
      >
        At least one search option must be checked.
      </span>
      <span id="search-input-label" class="sr-only">
        Search for students, courses, or notes.
        {{ searchInputRequired ? 'Input is required.' : '' }}
        {{ searchHistory.length ? 'Expect auto-suggest of previous searches.' : '' }}
        (Type / to put focus in the search input field.)
      </span>
      <div class="d-flex" :class="{'pb-3': showNoteFilters}">
        <div class="flex-grow-1">
          <InputAutocomplete
            id="search-students-input"
            aria-labelledby="search-input-label"
            :disabled="disabledSearch"
            :get-suggestions="filterSuggestions"
            :on-submit="search"
            placeholder="/ to search"
            :required="searchInputRequired"
            type="search"
          />
          <b-popover
            v-if="showErrorPopover"
            :show.sync="showErrorPopover"
            aria-live="polite"
            placement="top"
            role="alert"
            target="search-students-input"
          >
            <span id="popover-error-message" class="has-error"><font-awesome icon="exclamation-triangle" class="text-warning pr-1" /> Search input is required</span>
          </b-popover>
        </div>
        <div>
          <b-button
            id="go-search"
            class="btn-primary-color-override h-100 ml-1 mr-0"
            :disabled="disabledSearch"
            variant="primary"
            @keypress="onSubmit"
            @click.stop="onSubmit"
          >
            Go<span class="sr-only"> (submit search)</span>
          </b-button>
        </div>
      </div>
    </form>
    <hr v-if="showSearchOptions" class="ml-2 mr-2 section-divider" />
  </div>
</template>

<script>
import Autocomplete from '@/components/util/Autocomplete'
import Context from '@/mixins/Context'
import InputAutocomplete from '@/components/search/InputAutocomplete'
import Scrollable from '@/mixins/Scrollable'
import Util from '@/mixins/Util'
import {findStudentsByNameOrSid} from '@/api/student'
import {getAllTopics} from '@/api/topics'
import {addToSearchHistory, findAdvisorsByName, getMySearchHistory} from '@/api/search'

export default {
  name: 'SearchForm',
  components: {
    Autocomplete,
    InputAutocomplete
  },
  mixins: [Context, Scrollable, Util],
  props: {
    domain: {
      required: true,
      type: Array
    },
  },
  data() {
    return {
      defaultNoteFilters: {
        author: null,
        dateFrom: null,
        dateTo: null,
        postedBy: 'anyone',
        student: null,
        topic: null,
      },
      includeAdmits: this.domain.includes('admits'),
      includeCourses: this.domain.includes('courses'),
      includeNotes: this.domain.includes('notes'),
      includeStudents: this.domain.includes('students'),
      findAdvisorsByName: findAdvisorsByName,
      findStudentsByNameOrSid: findStudentsByNameOrSid,
      maxDate: new Date(),
      minDate: new Date('01/01/1900'),
      noteFilters: null,
      searchHistory: [],
      showNoteFilters: false,
      showErrorPopover: false,
      showSearchOptions: false,
      topicOptions: undefined
    }
  },
  computed: {
    allOptionsUnchecked() {
      return !this.includeCourses && !this.includeNotes && !this.includeStudents && (!this.domain.includes('admits') || !this.includeAdmits)
    },
    disabledSearch() {
      return this.validDateRange === false || this.allOptionsUnchecked
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
    showUncheckedOptionsAlert() {
      return this.showSearchOptions && this.allOptionsUnchecked
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
    domain(value) {
      this.includeAdmits = value.includes('admits')
      this.includeCourses = value.includes('courses')
      this.includeNotes = value.includes('notes')
      this.includeStudents = value.includes('students')
    },
    includeAdmits(value) {
      if (this.showSearchOptions) {
        this.$announcer.polite(`Search ${value ? 'will' : 'will not'} include admits.`)
      }
    },
    includeCourses(value) {
      this.$announcer.polite(`Search ${value ? 'will' : 'will not'} include courses.`)
    },
    includeNotes(value) {
      if (value) {
        this.$announcer.polite('Search will include notes and appointments.')
      } else {
        this.showNoteFilters = false
        this.$announcer.polite('Search will include neither notes nor appointments.')
      }
    },
    includeStudents(value) {
      if (this.showSearchOptions) {
        this.$announcer.polite(`Search ${value ? 'will' : 'will not'} include students.`)
      }
    },
    showNoteFilters(value) {
      if (value) {
        this.$announcer.polite('Notes and Appointments search filters opened.')
        this.$putFocusNextTick('search-option-note-filters-topic')
      }
      else {
        this.resetNoteFilters()
        this.$announcer.polite('Notes and Appointments search filters closed.')
        this.$putFocusNextTick('search-options-note-filters-toggle')
      }
    }
  },
  created() {
    this.resetNoteFilters()
    getMySearchHistory().then(history => {
      this.searchHistory = history
    })
    document.addEventListener('keydown', this.hideError)
    document.addEventListener('click', this.hideError)
  },
  methods: {
    clearAuthorFilter() {
      this.noteFilters.author = null
    },
    dateString(d, format) {
      return this.$options.filters.moment(d, format)
    },
    filterSuggestions(input) {
      const q = this.$_.trim(input && input.toLowerCase())
      return q.length ? this.searchHistory.filter(s => s.toLowerCase().startsWith(q)) : this.searchHistory
    },
    hideError() {
      this.showErrorPopover = false
    },
    onSubmit() {
      let el = document.getElementById('search-students-input')
      this.search(el && el.value)
    },
    resetNoteFilters() {
      this.noteFilters = this.$_.cloneDeep(this.defaultNoteFilters)
    },
    search(input) {
      const q = this.$_.trim(input)
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
          this.$_.noop
        )
        if (q) {
          addToSearchHistory(q).then(history => {
            this.searchHistory = history
          })
        }
      } else {
        this.showErrorPopover = true
        this.$announcer.polite('Search input is required')
        this.$putFocusNextTick('search-students-input')
      }
      this.scrollToTop()
    },
    toggleNoteFilters() {
      this.showNoteFilters = !this.showNoteFilters
      if (!this.topicOptions) {
        this.topicOptions = []
        getAllTopics(true).then(rows => {
          this.$_.each(rows, row => {
            const topic = row['topic']
            this.topicOptions.push({
              text: topic,
              value: topic
            })
          })
        })
      }
    },
    toggleSearchOptions() {
      this.showSearchOptions = !this.showSearchOptions
      if (this.showSearchOptions) {
        this.$announcer.polite('Search options opened')
        this.$putFocusNextTick('search-options-header')
      } else {
        this.resetNoteFilters()
        this.$announcer.polite('Search options closed')
        this.$putFocusNextTick('search-students-input')
      }
    }
  }
}
</script>

<style scoped>
.search-options-panel-toggle {
  color: #8bbdda;
  font-size: 12px;
}
.search-form-label {
  font-weight: 400;
  margin-bottom: 5px;
}
.search-input-date {
  margin-bottom: 10px;
}
.search-panel-feedback {
  color: #fff;
}
</style>
