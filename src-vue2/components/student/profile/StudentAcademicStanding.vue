<template>
  <div
    v-if="_get(standing, 'status') && standing.status !== 'GST'"
    class="student-academic-standing"
  >
    <span :id="`${rowIndex ? rowIndex + '-' : ''}academic-standing-term-${termId}`" class="red-flag-status">
      {{ config.academicStandingDescriptions[standing.status] || standing.status }} <span class="text-nowrap">({{ termName }})</span>
    </span>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {sisIdForTermName, termNameForSisId} from '@/berkeley'

export default {
  name: 'StudentAcademicStanding',
  mixins: [Context, Util],
  props: {
    rowIndex: {
      default: undefined,
      required: false,
      type: String
    },
    standing: {
      required: true,
      type: Object
    }
  },
  computed: {
    termId() {
      return this.standing.termId || sisIdForTermName(this.standing.termName)
    },
    termName() {
      return this.standing.termName || termNameForSisId(this.standing.termId)
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
