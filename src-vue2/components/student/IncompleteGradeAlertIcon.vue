<template>
  <font-awesome
    v-if="sectionsWithIncompleteStatus.length"
    :id="`term-${termId}-course-${index}-has-incomplete-status`"
    :aria-label="ariaLabel"
    class="has-error ml-1"
    icon="info-circle"
    :title="ariaLabel"
  />
</template>

<script>
import {getIncompleteGradeDescription, getSectionsWithIncompleteStatus} from '@/berkeley'

export default {
  name: 'IncompleteGradeAlertIcon',
  props: {
    course: {
      required: true,
      type: Object
    },
    index: {
      required: true,
      type: Number
    },
    termId: {
      required: true,
      type: String
    }
  },
  data: () => ({
    ariaLabel: undefined,
    sectionsWithIncompleteStatus: undefined
  }),
  created() {
    this.sectionsWithIncompleteStatus = getSectionsWithIncompleteStatus(this.course.sections)
    this.ariaLabel = getIncompleteGradeDescription(this.course.displayName, this.sectionsWithIncompleteStatus)
  }
}
</script>
