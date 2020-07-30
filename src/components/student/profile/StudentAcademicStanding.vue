<template>
  <div 
    v-if="get(standing, 'status') && standing.status !== 'GST'"
    class="student-academic-standing">
    <span :id="`${rowIndex ? rowIndex + '-' : ''}academic-standing-term-${termId || 'latest'}`" class="red-flag-status">
      {{ descriptions[standing.status] || standing.status }}
    </span>
  </div>
</template>

<script>
import Util from '@/mixins/Util';

export default {
  name: "StudentAcademicStanding",
  mixins: [Util],
  props: {
    standing: {
      required: true,
      type: Object
    },
    rowIndex: String,
    termId: String
  },
  data: () => ({
    descriptions: {
      'DIS': 'Dismissed',
      'PRO': 'Probation',
      'SUB': 'Subject to Dismissal'
    }
  })
}
</script>

<style>
.student-academic-standing {
  display: inline-block;
  margin-bottom: 5px;
}
</style>