<template>
  <div class="font-size-16 font-weight-bold">
    What is the extent of your search?
    <span
      v-if="!includeAdmits && !includeStudents && !includeCourses && !includeNotes"
      class="text-error"
    >
      Please select one or more.
    </span>
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
</template>

<script lang="ts">
import {useContextStore} from '@/stores/context'
import {useSearchStore} from '@/stores/search'
import {toRefs} from 'vue'

export default {
  setup() {
    const onChangeIncludeNotes = (include: boolean) => {
      if (!include) {
        const store = useSearchStore()
        store.setAuthor(null)
        store.setFromDate(null)
        store.setPostedBy('anyone')
        store.setStudent(null)
        store.setToDate(null)
        store.setTopic(null)
      }
    }
    const {domain, includeAdmits, includeStudents, includeCourses, includeNotes} = toRefs(useSearchStore())
    return {
      currentUser: useContextStore().currentUser,
      domain,
      onChangeIncludeNotes,
      includeAdmits,
      includeStudents,
      includeCourses,
      includeNotes
    }
  }
}
</script>
