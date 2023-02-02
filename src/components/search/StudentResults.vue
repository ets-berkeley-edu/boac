<template>
  <div>
    <h2 id="student-results-page-header" class="font-size-18">
      {{ pluralize('student', results.totalStudentCount) }}<span v-if="queryText">  matching '{{ queryText }}'</span>
    </h2>
    <div v-if="results.totalStudentCount > studentLimit" class="mb-2">
      Showing the first {{ studentLimit }} students.
    </div>
    <CuratedGroupSelector
      context-description="Search"
      domain="default"
      :students="results.students"
    />
    <SortableStudents
      domain="default"
      :students="results.students"
      :options="{
        includeCuratedCheckbox: true,
        sortBy: 'lastName',
        reverse: false
      }"
    />
  </div>
</template>

<script>
import CuratedGroupSelector from '@/components/curated/dropdown/CuratedGroupSelector'
import SearchSession from '@/mixins/SearchSession'
import Util from '@/mixins/Util'
import SortableStudents from '@/components/search/SortableStudents'

export default {
  name: 'StudentResults',
  mixins: [SearchSession, Util],
  components: {
    CuratedGroupSelector,
    SortableStudents,
  },
  props: {
    results: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    studentLimit: 50
  })
}
</script>
