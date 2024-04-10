<template>
  <v-icon
    v-if="sectionsWithIncompleteStatus.length"
    :id="`term-${termId}-course-${index}-has-incomplete-status`"
    :aria-label="ariaLabel"
    class="ml-1"
    color="error"
    :icon="mdiInformationOutline"
    :title="ariaLabel"
  />
</template>

<script setup>
import {mdiInformationOutline} from '@mdi/js'
</script>

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
