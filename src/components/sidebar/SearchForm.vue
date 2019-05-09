<template>
  <form
    id="search-students-form"
    autocomplete="off"
    class="m-2"
    :class="{'search-page-body': context === 'pageBody'}"
    @submit.prevent="search()">
    <div v-if="context === 'sidebar'" class="d-flex justify-content-between search-label text-nowrap text-white">
      <div>
        <i class="fas fa-search"></i>
        <label
          for="search-students-input"
          class="search-form-label pl-1">Search</label>
      </div>
      <b-btn
        id="search-options-panel-toggle"
        v-b-toggle="'search-options-panel'"
        class="pr-0 search-options-panel-toggle"
        variant="link"
        @click="showSearchOptions = !showSearchOptions">
        {{ showSearchOptions ? 'Hide' : 'Show' }} options
      </b-btn>
    </div>
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
        class="search-input w-100"
        :class="{ 'input-disabled': allOptionsUnchecked }"
        :readonly="allOptionsUnchecked"
        :aria-readonly="allOptionsUnchecked"
        aria-label="Hit enter to execute search"
        type="text"
        required
        maxlength="255" />
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
    <b-collapse v-if="context === 'sidebar'" id="search-options-panel" class="mt-1 text-white">
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
          Students (name or SID)
        </label>
      </div>
      <div class="d-flex">
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
      <div class="d-flex">
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
          v-if="includeNotes"
          id="search-options-note-filters-toggle"
          class="search-options-panel-toggle search-options-panel-toggle-subpanel"
          variant="link"
          @click="showNoteFilters = !showNoteFilters">
          ({{ showNoteFilters ? 'hide' : 'show' }} filters)
        </b-btn>
      </div>
      <b-collapse
        id="search-options-note-filters-subpanel"
        v-model="showNoteFilters"
        class="mt-2 text-white">
        <div>
          <b-form-group label="Posted By">
            <b-form-radio
              v-model="noteFilters.postedBy"
              name="note-filters-posted-by"
              value="anyone">
              Anyone
            </b-form-radio>
            <b-form-radio
              v-model="noteFilters.postedBy"
              name="note-filters-posted-by"
              value="you">
              You
            </b-form-radio>
          </b-form-group>
        </div>
        <b-button type="submit" variant="primary">Find notes</b-button>
      </b-collapse>
    </b-collapse>
  </form>
</template>

<script>
import Context from '@/mixins/Context';
import GoogleAnalytics from '@/mixins/GoogleAnalytics';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'SearchForm',
  mixins: [Context, GoogleAnalytics, UserMetadata, Util],
  props: {
    context: String,
    domain: Array,
  },
  data() {
    return {
      includeCourses: this.domain.includes('courses'),
      includeNotes: this.domain.includes('notes'),
      includeStudents: this.domain.includes('students'),
      noteFilters: {
        postedBy: 'anyone'
      },
      searchPhrase: null,
      showNoteFilters: false,
      showSearchOptions: false
    };
  },
  computed: {
    allOptionsUnchecked() {
      return this.showSearchOptions && !this.includeCourses && !this.includeNotes && !this.includeStudents;
    }
  },
  watch: {
    includeNotes: function(val) {
      if (!val) {
        this.showNoteFilters = false;
      }
    }
  },
  methods: {
    search() {
      this.searchPhrase = this.trim(this.searchPhrase);
      if (this.searchPhrase) {
        const query = {
          q: this.searchPhrase,
          courses: this.includeCourses,
          notes: this.includeNotes,
          students: this.includeStudents
        };
        if (this.includeNotes && this.noteFilters.postedBy === 'you') {
          query.authorCsid = this.user.csid;
        }
        this.$router.push({
          path: this.forceUniquePath('/search'),
          query: query
        });
        this.gaEvent(
          'Search',
          'submit',
          `courses: ${this.includeCourses}; notes: ${this.includeNotes}; students: ${this.includeStudents}`,
          this.searchPhrase
        );
      } else {
        this.alertScreenReader('Search input is required');
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
.search-label {
  align-items: baseline;
  font-size: 14px;
}
.search-options-panel-toggle {
  color: #8bbdda;
  font-size: 12px;
}
.search-options-panel-toggle-subpanel {
  padding-left: 5px;
}
.search-students-form-button {
  min-width: 200px;
}
.search-form-label {
  font-weight: 400;
}
.search-input {
  box-sizing: border-box;
  border: 2px solid #ccc;
  border-radius: 4px;
  color: #333;
  height: 45px;
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
</style>
