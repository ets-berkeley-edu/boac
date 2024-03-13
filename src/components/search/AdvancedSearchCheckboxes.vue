<template>
  <div class="pb-2">
    <div class="font-size-16 font-weight-bold">
      What is the extent of your search?
      <div
        class="font-size-14 font-weight-500 ml-2"
        :class="{'has-error': !includeAdmits && !includeStudents && !includeCourses && !includeNotes}"
      >
        Select one or more.
      </div>
    </div>
    <div class="align-center d-flex flex-wrap">
      <v-checkbox
        v-if="domain.includes('admits')"
        id="search-include-admits-checkbox"
        v-model="includeAdmits"
        color="primary"
        hide-details
        label="Students"
      >
        <template #label>
          <span class="sr-only">Search for</span>
          Admitted Students
        </template>
      </v-checkbox>
      <v-checkbox
        id="search-include-students-checkbox"
        v-model="includeStudents"
        color="primary"
        hide-details
      >
        <template #label>
          <span class="sr-only">Search for</span>
          Students
        </template>
      </v-checkbox>
      <v-checkbox
        v-if="domain.includes('courses')"
        id="search-include-courses-checkbox"
        v-model="includeCourses"
        color="primary"
        hide-details
      >
        <template #label>
          <span class="sr-only">Search for</span>
          Classes
        </template>
      </v-checkbox>
      <v-checkbox
        v-if="currentUser.canAccessAdvisingData"
        id="search-include-notes-checkbox"
        v-model="includeNotes"
        color="primary"
        hide-details
        @change="onChangeIncludeNotes"
      >
        <template #label>
          <span class="sr-only">Search for</span>
          Notes &amp; Appointments
        </template>
      </v-checkbox>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import SearchSession from '@/mixins/SearchSession'

export default {
  name: 'AdvancedSearchCheckboxes',
  mixins: [Context, SearchSession],
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
