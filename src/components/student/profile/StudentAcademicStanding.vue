<template>
  <div
    v-if="_get(standing, 'status') && standing.status !== 'GST'"
    class="student-academic-standing"
  >
    <span :id="`${rowIndex ? rowIndex + '-' : ''}academic-standing-term-${termId}`" class="red-flag-status">
      {{ $config.academicStandingDescriptions[standing.status] || standing.status }} <span class="text-nowrap">({{ termName }})</span>
    </span>
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley'
import Util from '@/mixins/Util'

export default {
  name: 'StudentAcademicStanding',
  mixins: [Berkeley, Util],
  props: {
    standing: {
      type: Object
    },
    rowIndex: String
  },
  computed: {
    termId() {
      return this.standing.termId || this.sisIdForTermName(this.standing.termName)
    },
    termName() {
      return this.standing.termName || this.termNameForSisId(this.standing.termId)
    }
  }
}
</script>

<style>
.student-academic-standing {
  display: inline-block;
  margin-bottom: 5px;
}
</style>
