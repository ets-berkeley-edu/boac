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
import Berkeley from '@/mixins/Berkeley'

export default {
  name: 'IncompleteGradeAlertIcon',
  mixins: [Berkeley],
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
    this.sectionsWithIncompleteStatus = this.getSectionsWithIncompleteStatus(this.course.sections)
    this.ariaLabel = this.getIncompleteGradeDescription(this.course.displayName, this.sectionsWithIncompleteStatus)
  }
}
</script>
