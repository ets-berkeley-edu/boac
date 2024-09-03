<template>
  <v-icon
    :id="`term-${termId}-course-${index}-has-incomplete-status`"
    :aria-label="ariaLabel"
    class="ml-1"
    color="error"
    :icon="mdiInformationOutline"
    :title="ariaLabel"
  />
</template>

<script setup>
import {getIncompleteGradeDescription, getSectionsWithIncompleteStatus} from '@/berkeley'
import {mdiInformationOutline} from '@mdi/js'

const props = defineProps({
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
})

const sectionsWithIncompleteStatus = getSectionsWithIncompleteStatus(props.course.sections)
const ariaLabel = getIncompleteGradeDescription(props.course.displayName, sectionsWithIncompleteStatus)
</script>
