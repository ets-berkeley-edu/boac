<template>
  <div>
    <form
      id="search-students-form"
      :class="{'search-page-body': context === 'pageBody'}"
      class="search-form">
      <div class="d-flex flex-column-reverse">
        <div :class="{'search-form-button': context === 'pageBody'}">
          <span
            v-if="allOptionsUnchecked"
            class="sr-only"
            aria-live="polite"
            role="alert">
            At least one search option must be checked.
          </span>
          <Autocomplete
            id="search-students"
            ref="searchInput"
            v-model="searchPhrase"
            :demo-mode-blur="false"
            :restrict="false"
            :disabled="allOptionsUnchecked"
            :source="searchSuggestions"
            :input-class="allOptionsUnchecked ? 'input-disabled search-input' : 'search-input'"
            :is-required="searchInputRequired"
            :on-esc-form-input="hideError"
            :suggest-when="() => true"
            suggestion-label-class="suggestion-label"
            aria-label="Hit enter to execute search"
            type="text"
            maxlength="255" />
          <b-popover
            v-if="showErrorPopover"
            :show.sync="showErrorPopover"
            aria-live="polite"
            placement="top"
            role="alert"
            target="search-students-input">
            <span id="popover-error-message" class="has-error"><font-awesome icon="exclamation-triangle" class="text-warning pr-1" /> Search input is required</span>
          </b-popover>
        </div>
        <div v-if="context === 'sidebar'" class="d-flex flex-wrap justify-content-between search-label text-nowrap text-white">
          <div>
            <font-awesome icon="search" />
            <label
              for="search-students-input"
              class="search-form-label pl-1">Search</label>
          </div>
          <b-btn
            id="search-options-panel-toggle"
            v-b-toggle="'search-options-panel'"
            class="pr-0 pt-0 search-options-panel-toggle"
            variant="link"
            @click="toggleSearchOptions">
            {{ showSearchOptions ? 'Hide' : 'Show' }} options
          </b-btn>
        </div>
      </div>
      <div v-if="context === 'pageBody'">
        <b-btn
          id="search-students-button"
          variant="primary"
          class="btn-search-students btn-primary-color-override"
          type="submit">
          Search
        </b-btn>
      </div>
      <b-collapse
        v-if="context === 'sidebar'"
        id="search-options-panel"
        v-model="showSearchOptions"
        class="mt-2 text-white">
        <div v-if="domain.includes('admits')" class="d-flex">
          <b-form-checkbox
            id="search-include-admits-checkbox"
            v-model="includeAdmits"
            plain>
          </b-form-checkbox>
          <label
            for="search-include-admits-checkbox"
            class="search-form-label">
            <span class="sr-only">Search for</span>
            Admitted Students
          </label>
        </div>
        <div class="d-flex">
          <b-form-checkbox
            id="search-include-students-checkbox"
            v-model="includeStudents"
            plain>
          </b-form-checkbox>
          <label
            for="search-include-students-checkbox"
            class="search-form-label">
            <span class="sr-only">Search for</span>
            Students
          </label>
        </div>
        <div v-if="domain.includes('courses')" class="d-flex">
          <b-form-checkbox
            id="search-include-courses-checkbox"
            v-model="includeCourses"
            plain>
          </b-form-checkbox>
          <label
            for="search-include-courses-checkbox"
            class="search-form-label">
            <span class="sr-only">Search for</span>
            Classes
          </label>
        </div>
        <div v-if="$currentUser.canAccessAdvisingData" class="d-flex flex-wrap">
          <b-form-checkbox
            id="search-include-notes-checkbox"
            v-model="includeNotes"
            plain>
          </b-form-checkbox>
          <label
            for="search-include-notes-checkbox"
            class="search-form-label">
            <span class="sr-only">Search for</span>
            Notes &amp; Appointments
          </label>
          <b-btn
            id="search-options-note-filters-toggle"
            :class="includeNotes ? 'visible' : 'invisible'"
            class="search-options-panel-toggle search-options-panel-toggle-subpanel text-nowrap"
            variant="link"
            @click="toggleNoteFilters">
            ({{ showNoteFilters ? 'hide' : 'show' }} filters)
          </b-btn>
        </div>
        <b-collapse
          v-if="$currentUser.canAccessAdvisingData"
          id="search-options-note-filters-subpanel"
          v-model="showNoteFilters"
          class="search-options-note-filters-subpanel text-white">
          <div>
            <b-form-group label="Topic" label-for="search-option-note-filters-topic">
              <b-form-select
                id="search-option-note-filters-topic"
                v-model="noteFilters.topic"
                :options="topicOptions">
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
                @change.native="clearAuthorFilter">
                Anyone
              </b-form-radio>
              <b-form-radio
                id="search-options-note-filters-posted-by-you"
                v-model="noteFilters.postedBy"
                :ischecked="noteFilters.postedBy === 'you'"
                name="note-filters-posted-by"
                value="you"
                @change.native="clearAuthorFilter">
                You
              </b-form-radio>
            </b-form-group>
            <b-form-group label="Advisor" label-for="search-options-note-filters-author-input">
              <Autocomplete
                id="search-options-note-filters-author"
                v-model="noteAuthor"
                :source="findAdvisorsByName"
                :disabled="noteFilters.postedBy === 'you'"
                :placeholder="noteFilters.postedBy === 'you' ? $currentUser.name : 'Enter name...'">
              </Autocomplete>
            </b-form-group>
            <b-form-group label="Student (name or SID)" label-for="search-options-note-filters-student-input">
              <Autocomplete
                id="search-options-note-filters-student"
                v-model="noteFilters.student"
                :demo-mode-blur="true"
                :source="findStudentsByNameOrSid"
                placeholder="Enter name or SID...">
              </Autocomplete>
            </b-form-group>
            <b-form-group label="Date Range">
              <label
                for="search-options-note-filters-last-updated-from"
                class="search-form-label">
                <span class="sr-only">Date</span>
                From
              </label>
              <v-date-picker
                v-model="noteFilters.dateFrom"
                popover-visibility="focus"
                mode="single">
                <template v-slot="{inputValue, updateValue}">
                  <b-input-group>
                    <b-form-input
                      id="search-options-note-filters-last-updated-from"
                      :value="inputValue"
                      :formatter="dateFormat"
                      type="text"
                      name="note-filters-date-from"
                      class="search-input-date"
                      placeholder="MM/DD/YYYY"
                      expanded
                      lazy-formatter
                      @change.native="updateValue($event.target.value)">
                    </b-form-input>
                    <b-btn
                      v-if="noteFilters.dateFrom"
                      id="search-options-note-filters-last-updated-from-clear"
                      class="search-input-date"
                      @click="noteFilters.dateFrom = null">
                      <font-awesome icon="times" />
                      <span class="sr-only">Clear date from</span>
                    </b-btn>
                  </b-input-group>
                </template>
              </v-date-picker>
              <label
                for="search-options-note-filters-last-updated-to"
                class="search-form-label">
                <span class="sr-only">Date</span>
                To
              </label>
              <v-date-picker
                v-model="noteFilters.dateTo"
                popover-visibility="focus"
                mode="single">
                <template v-slot="{inputValue, updateValue}">
                  <b-input-group>
                    <b-form-input
                      id="search-options-note-filters-last-updated-to"
                      :value="inputValue"
                      :formatter="dateFormat"
                      type="text"
                      name="note-filters-date-to"
                      class="search-input-date"
                      placeholder="MM/DD/YYYY"
                      expanded
                      lazy-formatter
                      @change.native="updateValue($event.target.value)">
                    </b-form-input>
                    <b-btn
                      v-if="noteFilters.dateTo"
                      id="search-options-note-filters-last-updated-to-clear"
                      class="search-input-date"
                      @click="noteFilters.dateTo = null">
                      <font-awesome icon="times"></font-awesome>
                      <span class="sr-only">Clear date to</span>
                    </b-btn>
                  </b-input-group>
                </template>
              </v-date-picker>
              <b-form-invalid-feedback :state="validDateRange" class="search-panel-feedback">
                <font-awesome icon="exclamation-triangle" class="text-warning pr-1" />
                "To" must be later than or equal to "From."
              </b-form-invalid-feedback>
            </b-form-group>
          </div>
        </b-collapse>
        <b-button
          :disabled="validDateRange === false"
          variant="primary"
          @click.stop="search">
          Search
        </b-button>
      </b-collapse>
    </form>
    <hr v-if="showSearchOptions" class="ml-2 mr-2 section-divider" />
  </div>
</template>

<script>
import Autocomplete from '@/components/util/Autocomplete';
import Context from '@/mixins/Context';
import Scrollable from '@/mixins/Scrollable';
import Util from '@/mixins/Util';
import { findStudentsByNameOrSid } from '@/api/student';
import { getAllTopics } from '@/api/topics';
import { addToSearchHistory, findAdvisorsByName, getMySearchHistory } from '@/api/search';

export default {
  name: 'SearchForm',
  components: {
    Autocomplete
  },
  mixins: [Context, Scrollable, Util],
  props: {
    context: {
      required: true,
      type: String
    },
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
      noteFilters: null,
      searchHistory: [],
      searchPhrase: null,
      showNoteFilters: false,
      showErrorPopover: false,
      showSearchOptions: false,
      topicOptions: undefined
    };
  },
  computed: {
    allOptionsUnchecked() {
      return this.showSearchOptions && !this.includeAdmits && !this.includeCourses && !this.includeNotes && !this.includeStudents;
    },
    noteAuthor: {
      get: function() {
        if (this.noteFilters && this.noteFilters.postedBy === 'anyone') {
          return this.noteFilters.author;
        } else {
          return null;
        }
      },
      set: function(newValue) {
        this.noteFilters.postedBy = 'anyone';
        this.noteFilters.author = newValue;
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
      ));
    },
    validDateRange() {
      if (!this.noteFilters.dateFrom || !this.noteFilters.dateTo) {
        return null;
      } else if (this.noteFilters.dateTo < this.noteFilters.dateFrom) {
        return false;
      } else {
        return null;
      }
    }
  },
  watch: {
    domain(value) {
      this.includeAdmits = value.includes('admits');
      this.includeCourses = value.includes('courses');
      this.includeNotes = value.includes('notes');
      this.includeStudents = value.includes('students');
    },
    includeAdmits(value) {
      this.alertScreenReader(`Search ${value ? 'will' : 'will not'} include admits.`);
    },
    includeCourses(value) {
      this.alertScreenReader(`Search ${value ? 'will' : 'will not'} include courses.`);
    },
    includeNotes(value) {
      if (value) {
        this.alertScreenReader('Search will include notes and appointments.');
      } else {
        this.showNoteFilters = false;
        this.alertScreenReader('Search will include neither notes nor appointments.');
      }
    },
    includeStudents(value) {
      this.alertScreenReader(`Search ${value ? 'will' : 'will not'} include students.`);
    },
    searchPhrase() {
      this.search();
    },
    showNoteFilters(value) {
      if (value) {
        this.alertScreenReader('Notes and Appointments search filters opened.');
        this.putFocusNextTick('search-option-note-filters-topic');
      }
      else {
        this.resetNoteFilters();
        this.alertScreenReader('Notes and Appointments search filters closed.');
        this.putFocusNextTick('search-options-note-filters-toggle');
      }
    }
  },
  created() {
    this.resetNoteFilters();
    getMySearchHistory().then(history => {
      this.searchHistory = history;
    });
    document.addEventListener('keydown', this.hideError);
    document.addEventListener('click', this.hideError);
  },
  methods: {
    dateFormat(value) {
      const parsed = Date.parse(value);
      if (isNaN(parsed)) {
        return null;
      } else {
        return this.dateString(parsed, 'MM/DD/YYYY');
      }
    },
    clearAuthorFilter() {
      this.noteFilters.author = null;
    },
    dateString(d, format) {
      return this.$options.filters.moment(d, format);
    },
    hideError() {
      this.showErrorPopover = false;
    },
    searchSuggestions(q) {
      return new Promise(resolve => {
        let suggestions;
        if (q) {
          const normalized = q.toLowerCase();
          suggestions = this.filterList(this.searchHistory, s => s.toLowerCase().startsWith(normalized));
        } else {
          suggestions = this.searchHistory;
        }
        resolve(this.map(suggestions, s => {
          return { label: s }
        }))
      });
    },
    resetNoteFilters() {
      this.noteFilters = this.cloneDeep(this.defaultNoteFilters);
    },
    search() {
      const searchPhrase = this.trim(this.$refs.searchInput.getQuery());
      if (searchPhrase || !this.searchInputRequired) {
        const query = {
          notes: this.includeNotes,
          students: this.includeStudents
        };
        if (this.includeAdmits) {
          query.admits = this.includeAdmits;
        }
        if (this.includeCourses) {
          query.courses = this.includeCourses;
        }
        if (searchPhrase) {
          query.q = searchPhrase;
        }
        if (this.includeNotes) {
          if (this.noteFilters.postedBy === 'you') {
            query.advisorCsid = this.$currentUser.csid;
          } else if (this.noteFilters.author) {
            query.advisorCsid = this.noteFilters.author.sid;
            query.advisorUid = this.noteFilters.author.uid;
          }
          if (this.noteFilters.student) {
            query.studentCsid = this.noteFilters.student.sid;
          }
          if (this.noteFilters.topic) {
            query.noteTopic = this.noteFilters.topic;
          }
          if (this.noteFilters.dateFrom) {
            query.noteDateFrom = this.dateString(this.noteFilters.dateFrom, 'YYYY-MM-DD');
          }
          if (this.noteFilters.dateTo) {
            query.noteDateTo = this.dateString(this.noteFilters.dateTo, 'YYYY-MM-DD');
          }
        }
        this.$router.push(
          {
            path: '/search',
            query: query
          },
          this.noop
        );
        if (this.trim(searchPhrase)) {
          addToSearchHistory(searchPhrase).then(history => {
            this.searchHistory = history;
          });
        }
      } else {
        this.alertScreenReader('Search input is required');
        this.showErrorPopover = true;
        this.putFocusNextTick('search-students-input');
      }
      this.scrollToTop();
    },
    toggleNoteFilters() {
      this.showNoteFilters = !this.showNoteFilters;
      if (!this.topicOptions) {
        this.topicOptions = [];
        getAllTopics(true).then(rows => {
          this.each(rows, row => {
            const topic = row['topic']
            this.topicOptions.push({
              text: topic,
              value: topic
            })
          });
        });
      }
    },
    toggleSearchOptions() {
      this.showSearchOptions = !this.showSearchOptions;
      if (this.showSearchOptions) {
        this.alertScreenReader('Search options opened');
        this.putFocusNextTick('search-include-students-checkbox');
      } else {
        this.resetNoteFilters();
        this.alertScreenReader('Search options closed');
        this.putFocusNextTick('search-students-input');
      }
    }
  }
};
</script>

<style>
.search-input {
  box-sizing: border-box !important;
  border: 2px solid #ccc !important;
  border-radius: 4px !important;
  color: #333;
  height: 45px !important;
  padding: 0 10px 0 10px !important;
}
.suggestion-label {
  display: inline-block;
  max-width: 100vw;
  overflow-wrap: break-word;
  white-space: normal;
}
</style>

<style scoped>
.btn-search-students {
  height: 46px;
}
.input-disabled {
  background: #ddd;
}
.search-form {
  margin: 10px 10px 15px 15px;
}
.search-label {
  align-items: baseline;
  font-size: 14px;
}
.search-options-panel-toggle {
  color: #8bbdda;
  font-size: 12px;
}
.search-options-panel-toggle-subpanel {
  margin-bottom: .5rem;
  padding: 0 0 0 5px;
}
.search-form-label {
  font-weight: 400;
  margin-bottom: 5px;
}
.search-input-date {
  margin-bottom: 10px;
}
.search-options-note-filters-subpanel {
  margin-left: 20px;
}
.search-page-body {
  align-items: center;
  display: flex;
  flex-flow: row wrap;
  margin-top: 10px;
}
.search-page-body div {
  align-self: flex-end;
}
.search-page-body div:first-child {
  padding-right: 15px;
}
.search-panel-feedback {
  color: #fff;
}
</style>
