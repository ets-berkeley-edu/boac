<template>
  <div class="pb-2">
    <div class="font-size-16 font-weight-700 search-form-label">
      What is the extent of your search?
      <div
        class="font-size-14 font-weight-500 ml-2"
        :class="{'has-error': !includeAdmits && !includeStudents && !includeCourses && !includeNotes}"
      >
        Select one or more.
      </div>
    </div>
    <div class="align-items-center d-flex flex-wrap ml-2">
      <div v-if="domain.includes('admits')" class="align-items-center d-flex mr-3">
        <b-checkbox
          id="search-include-admits-checkbox"
          v-model="includeAdmits"
          class="z-index-0"
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
          v-model="includeStudents"
          class="z-index-0"
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
          v-model="includeCourses"
          class="z-index-0"
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
          v-model="includeNotes"
          class="z-index-0"
          @change="onChangeIncludeNotes"
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
import SearchSession from '@/mixins/SearchSession'

export default {
  name: 'AdvancedSearchCheckboxes',
  mixins: [SearchSession],
  methods: {
    onChangeIncludeNotes(include) {
      if (!include) {
        this.author = null
        this.fromDate = null
        this.postedBy = 'anyone'
        this.student = null
        this.toDate = null
        this.topic = null
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
