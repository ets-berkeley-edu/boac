<template>
  <div class="pb-2">
    <div class="font-size-16 font-weight-700 search-form-label">
      What is the extent of your search?
      <div
        class="font-size-14 font-weight-500 ml-2"
        :class="{'has-error': !admits && !students && !courses && !notes}"
      >
        Select one or more.
      </div>
    </div>
    <div class="align-items-center d-flex flex-wrap ml-2">
      <div v-if="domain.includes('admits')" class="align-items-center d-flex mr-3">
        <b-checkbox
          id="search-include-admits-checkbox"
          v-model="admits"
          plain
        />
        <label
          for="search-include-admits-checkbox"
          class="search-form-label"
        >
          <span class="sr-only">Search for</span>
          Admitted Students
        </label>
      </div>
      <div class="align-items-center d-flex mr-3">
        <b-checkbox
          id="search-include-students-checkbox"
          v-model="students"
          plain
        />
        <label
          for="search-include-students-checkbox"
          class="search-form-label"
        >
          <span class="sr-only">Search for</span>
          Students
        </label>
      </div>
      <div v-if="domain.includes('courses')" class="align-items-center d-flex mr-3">
        <b-checkbox
          id="search-include-courses-checkbox"
          v-model="courses"
          plain
        />
        <label
          for="search-include-courses-checkbox"
          class="search-form-label"
        >
          <span class="sr-only">Search for</span>
          Classes
        </label>
      </div>
      <div v-if="$currentUser.canAccessAdvisingData" class="align-items-center d-flex mr-3">
        <b-checkbox
          id="search-include-notes-checkbox"
          v-model="notes"
          plain
        />
        <label
          for="search-include-notes-checkbox"
          class="search-form-label"
        >
          <span class="sr-only">Search for</span>
          Notes &amp; Appointments
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import Search from '@/mixins/Search'

export default {
  name: 'AdvancedSearchCheckboxes',
  mixins: [Search],
  computed: {
    admits: {
      get: function() {
        return this.domain.includes('admits') && this.includeAdmits
      },
      set: function(value) {
        this.setIncludeAdmits(value)
      }
    },
    courses: {
      get: function() {
        return this.includeCourses
      },
      set: function(value) {
        this.setIncludeCourses(value)
      }
    },
    notes: {
      get: function() {
        return this.includeNotes
      },
      set: function(value) {
        this.setIncludeNotes(value)
      }
    },
    students: {
      get: function() {
        return this.includeStudents
      },
      set: function(value) {
        this.setIncludeStudents(value)
      }
    }
  }
}
</script>

<style scoped>
.search-form-label {
  margin-bottom: 2px;
}
</style>
