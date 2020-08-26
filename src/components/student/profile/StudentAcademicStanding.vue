<template>
  <div
    v-if="$_.get(standing, 'status') && standing.status !== 'GST'"
    class="student-academic-standing">
    <span :id="`${rowIndex ? rowIndex + '-' : ''}academic-standing-term-${standing.termId}`" class="red-flag-status">
      {{ $config.academicStandingDescriptions[standing.status] || standing.status }} ({{ termNameForSisId(standing.termId) }})
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
  }
}
</script>

<style>
.student-academic-standing {
  display: inline-block;
  margin-bottom: 5px;
}
</style>
