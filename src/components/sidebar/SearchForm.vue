<template>
  <div>
    <form
      id="search-students-form"
      autocomplete="off"
      class="search-form"
      :class="{'search-page-body': context === 'pageBody'}"
      @keypress.enter.stop="search()"
      @submit.prevent="search()">
      <div class="d-flex flex-column-reverse">
        <div :class="{'search-form-button': context === 'pageBody'}">
          <span
            v-if="allOptionsUnchecked"
            class="sr-only"
            aria-live="polite"
            role="alert">
            At least one search option must be checked.
          </span>
          <input
            id="search-students-input"
            v-model="searchPhrase"
            class="pl-2 pr-2 search-input w-100"
            :class="{ 'input-disabled': allOptionsUnchecked }"
            :readonly="allOptionsUnchecked"
            :aria-readonly="allOptionsUnchecked"
            aria-label="Hit enter to execute search"
            type="text"
            :required="searchInputRequired"
            maxlength="255" />
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
            @click="toggleSearchOptions()">
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
      <b-collapse v-if="context === 'sidebar'" id="search-options-panel" class="mt-2 text-white">
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
        <div class="d-flex flex-wrap">
          <b-form-checkbox
            id="search-include-notes-checkbox"
            v-model="includeNotes"
            plain>
          </b-form-checkbox>
          <label
            for="search-include-notes-checkbox"
            class="search-form-label">
            <span class="sr-only">Search for</span>
            Notes
          </label>
          <b-btn
            id="search-options-note-filters-toggle"
            class="search-options-panel-toggle search-options-panel-toggle-subpanel text-nowrap"
            variant="link"
            :class="includeNotes ? 'visible' : 'invisible'"
            @click="toggleNoteFilters()">
            ({{ showNoteFilters ? 'hide' : 'show' }} filters)
          </b-btn>
        </div>
        <b-collapse
          id="search-options-note-filters-subpanel"
          v-model="showNoteFilters"
          class="search-options-note-filters-subpanel text-white">
          <div>
            <b-form-group label="Topic">
              <b-form-select
                id="search-option-note-filters-topic"
                v-model="noteFilters.topic"
                :options="topicOptions">
              </b-form-select>
            </b-form-group>
            <b-form-group label="Posted By">
              <b-form-radio
                id="search-options-note-filters-posted-by-anyone"
                v-model="noteFilters.postedBy"
                name="note-filters-posted-by"
                value="anyone"
                :ischecked="noteFilters.postedBy === 'anyone'"
                @change.native="clearAuthorFilter">
                Anyone
              </b-form-radio>
              <b-form-radio
                id="search-options-note-filters-posted-by-you"
                v-model="noteFilters.postedBy"
                name="note-filters-posted-by"
                value="you"
                :ischecked="noteFilters.postedBy === 'you'"
                @change.native="clearAuthorFilter">
                You
              </b-form-radio>
            </b-form-group>
            <b-form-group label="Advisor">
              <Autocomplete
                id="search-options-note-filters-author"
                v-model="noteAuthor"
                :source="findAuthorsByName"
                :disabled="noteFilters.postedBy === 'you'"
                :placeholder="noteFilters.postedBy === 'you' ? user.name : 'Enter name...'">
              </Autocomplete>
            </b-form-group>
            <b-form-group label="Student (name or SID)">
              <Autocomplete
                id="search-options-note-filters-student"
                v-model="noteFilters.student"
                :demo-mode-blur="true"
                :source="findStudentsByNameOrSid"
                placeholder="Enter name or SID...">
              </Autocomplete>
            </b-form-group>
            <b-form-group label="Last Updated">
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
                      type="text"
                      name="note-filters-date-from"
                      class="search-input-date"
                      :value="inputValue"
                      :formatter="dateFormat"
                      placeholder="MM/DD/YYYY"
                      expanded
                      lazy-formatter
                      @change.native="updateValue($event.target.value)">
                    </b-form-input>
                    <b-btn
                      v-if="noteFilters.dateFrom"
                      id="search-options-note-filters-last-updated-from-clear"
                      class="search-input-date"
                      @click="noteFilters.dateFrom = null;">
                      <font-awesome icon="times"></font-awesome>
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
                      type="text"
                      name="note-filters-date-to"
                      class="search-input-date"
                      :value="inputValue"
                      :formatter="dateFormat"
                      placeholder="MM/DD/YYYY"
                      expanded
                      lazy-formatter
                      @change.native="updateValue($event.target.value)">
                    </b-form-input>
                    <b-btn
                      v-if="noteFilters.dateTo"
                      id="search-options-note-filters-last-updated-to-clear"
                      class="search-input-date"
                      @click="noteFilters.dateTo = null;">
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
          type="submit"
          variant="primary"
          :disabled="validDateRange === false">
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
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { getTopics, findAuthorsByName } from '@/api/notes';
import { findStudentsByNameOrSid } from '@/api/student';

export default {
  name: 'SearchForm',
  components: {
    Autocomplete
  },
  mixins: [Context, UserMetadata, Util],
  props: {
    context: String,
    domain: Array,
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
      includeCourses: this.domain.includes('courses'),
      includeNotes: this.domain.includes('notes'),
      includeStudents: this.domain.includes('students'),
      findAuthorsByName: findAuthorsByName,
      findStudentsByNameOrSid: findStudentsByNameOrSid,
      noteFilters: null,
      searchPhrase: null,
      showNoteFilters: false,
      showSearchOptions: false,
      topicOptions: undefined
    };
  },
  computed: {
    allOptionsUnchecked() {
      return this.showSearchOptions && !this.includeCourses && !this.includeNotes && !this.includeStudents;
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
      if (this.includeNotes && (
        this.noteFilters.author ||
        this.noteFilters.dateFrom ||
        this.noteFilters.dateTo ||
        this.noteFilters.postedBy !== 'anyone' ||
        this.noteFilters.student ||
        this.noteFilters.topic
      )) {
        return false;
      } else {
        return true;
      }
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
    includeNotes: function(val) {
      if (!val) {
        this.showNoteFilters = false;
      }
    }
  },
  created() {
    this.resetNoteFilters();
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
    resetNoteFilters() {
      this.noteFilters = this.cloneDeep(this.defaultNoteFilters);
    },
    search() {
      this.searchPhrase = this.trim(this.searchPhrase);
      if (this.searchPhrase || !this.searchInputRequired) {
        const query = {
          notes: this.includeNotes,
          students: this.includeStudents
        };
        if (this.domain.includes('courses')) {
          query.courses = this.includeCourses;
        }
        if (this.searchPhrase) {
          query.q = this.searchPhrase;
        }
        if (this.includeNotes) {
          if (this.noteFilters.postedBy === 'you') {
            query.authorCsid = this.user.csid;
          } else if (this.noteFilters.author) {
            query.authorCsid = this.noteFilters.author.sid;
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
        this.$router.push({
          path: `/search`,
          query: query
        });
        this.gaSearchEvent(`Search with courses: ${this.includeCourses}; notes: ${this.includeNotes}; students: ${this.includeStudents}`);
      } else {
        this.alertScreenReader('Search input is required');
      }
    },
    toggleNoteFilters() {
      this.showNoteFilters = !this.showNoteFilters;
      if (!this.showNoteFilters) {
        this.resetNoteFilters();
      }
      if (!this.topicOptions) {
        this.topicOptions = [
          {text: 'Any topic', value: null}
        ];
        getTopics(true).then(data => {
          this.each(data, topic => {
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
        this.putFocusNextTick('search-include-students-checkbox');
      } else {
        this.resetNoteFilters();
        this.putFocusNextTick('search-students-input');
      }
    }
  }
};
</script>

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
.search-input {
  box-sizing: border-box;
  border: 2px solid #ccc;
  border-radius: 4px;
  color: #333;
  height: 45px;
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
