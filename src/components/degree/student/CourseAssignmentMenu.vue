<template>
  <v-menu
    :id="`assign-course-${course.id}-dropdown`"
    :disabled="degreeStore.disableButtons || isSaving"
    transition="slide-y-transition"
  >
    <template #activator="{props}">
      <v-btn
        :id="`assign-course-${course.id}-btn`"
        :aria-label="`${course.name} category options`"
        :class="{
          'accent-blue': course.accentColor === 'Blue',
          'accent-green': course.accentColor === 'Green',
          'accent-orange': course.accentColor === 'Orange',
          'accent-purple': course.accentColor === 'Purple',
          'accent-red': course.accentColor === 'Red',
          'bg-transparent text-primary': !degreeStore.disableButtons,
          'text-surface-variant': !course.accentColor,
          'text-white': degreeStore.draggingCourseId === course.id
        }"
        density="compact"
        flat
        :icon="mdiDrag"
        v-bind="props"
      />
    </template>
    <v-list class="py-4" variant="flat">
      <v-list-item-action v-if="course.categoryId || course.ignore">
        <v-btn
          id="assign-course-to-option-null"
          class="font-italic"
          color="primary"
          density="comfortable"
          variant="text"
          @click="onSelect(null, false)"
        >
          <span aria-hidden="true">-- </span>Unassign<span aria-hidden="true"> --</span>
        </v-btn>
      </v-list-item-action>
      <v-list-item-action v-if="!course.ignore">
        <v-btn
          id="course-to-option-ignore"
          class="font-italic"
          color="primary"
          density="comfortable"
          variant="text"
          @click="onSelect(null, true)"
        >
          <span aria-hidden="true">-- </span>{{ junkDrawerName }}<span aria-hidden="true"> --</span>
        </v-btn>
      </v-list-item-action>
      <hr class="my-2" />
      <v-list-item-action v-for="option in options" :key="option.id">
        <v-btn
          :id="`assign-course-to-option-${option.id}`"
          :class="{
            'font-size-16 mr-4': option.categoryType === 'Category',
            'font-size-15 ml-2 mr-4': option.categoryType === 'Subcategory',
            'font-size-12 mx-4': isCourseRequirement(option) || isCampusRequirement(option)
          }"
          color="primary"
          :disabled="option.disabled"
          variant="text"
          @click="onSelect(option, false)"
        >
          <span v-if="!option.disabled" class="sr-only">Move to </span>
          <span class="sr-only">{{ option.lineage }}</span>
          {{ option.name }}
          <span v-if="option.disabled" class="sr-only"> (disabled)</span>
        </v-btn>
      </v-list-item-action>
    </v-list>
  </v-menu>
</template>

<script setup>
import {alertScreenReader} from '@/lib/utils'
import {assignCourse} from '@/api/degree'
import {categoryHasCourse, isCampusRequirement} from '@/lib/degree-progress'
import {cloneDeep, each, every, includes, isEmpty} from 'lodash'
import {computed, ref} from 'vue'
import {mdiDrag} from '@mdi/js'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {useDegreeStore} from '@/stores/degree-edit-session/index'

const degreeStore = useDegreeStore()

const props = defineProps({
  course: {
    required: true,
    type: Object
  },
  afterCourseAssignment: {
    default: () => {},
    required: false,
    type: Function
  }
})

const isSaving = ref(false)
const junkDrawerName = 'Other Coursework'

const options = computed(() => {
  const put = (option, parent, grandparent) => {
    option.disabled = (isCourseRequirement(option) && !!option.courses.length)
      || (option.categoryType === 'Category' && !!option.subcategories.length)
      || categoryHasCourse(option, props.course)
    option.lineage = grandparent ? `${grandparent.name} ${parent.name}` : (parent ? parent.name : '')
    if ((!option.disabled || !isCourseRequirement(option)) && !isCampusRequirements(option)) {
      options.push(option)
    }
  }
  const options = []
  each(cloneDeep(degreeStore.categories), category => {
    put(category)
    each(category.courseRequirements, courseRequirement => put(courseRequirement, category))
    each(category.subcategories, subcategory => {
      put(subcategory, category)
      each(subcategory.courseRequirements, course => put(course, subcategory, category))
    })
  })
  return options
})

const isCampusRequirements = option => {
  return isCampusRequirement(option)
    || (!isEmpty(option.courseRequirements) && every(option.courseRequirements, isCampusRequirement))
}

const isCourseRequirement = option => {
  return includes(['Course Requirement', 'Placeholder: Course Copy'], option.categoryType)
}

const onSelect = (category, ignore) => {
  degreeStore.setDisableButtons(true)
  const categoryId = category && category.id
  assignCourse(props.course.id, categoryId, ignore).then(() => {
    refreshDegreeTemplate(degreeStore.templateId).then(courseAssigned => {
      degreeStore.setDisableButtons(false)
      if (category) {
        alertScreenReader(`${category.name} selected for ${props.course.name}`)
      } else {
        alertScreenReader(`Moved to ${ignore ? props.junkDrawerName : 'Unassigned'}`)
      }
      props.afterCourseAssignment(courseAssigned)
    })
  })
}
</script>
