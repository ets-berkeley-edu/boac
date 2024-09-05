<template>
  <v-menu
    :id="`assign-course-${course.id}-dropdown`"
    v-model="selectedOption"
    :disabled="degreeStore.disableButtons || isSaving"
    transition="slide-y-transition"
  >
    <template #activator="{props}">
      <v-btn
        :id="`assign-course-${course.id}-btn`"
        :aria-label="`${course.name} category options`"
        :class="{
          'accent-color-blue': course.accentColor === 'Blue',
          'accent-color-green': course.accentColor === 'Green',
          'accent-color-orange': course.accentColor === 'Orange',
          'accent-color-purple': course.accentColor === 'Purple',
          'accent-color-red': course.accentColor === 'Red',
          'bg-transparent text-primary': !degreeStore.disableButtons,
          'text-grey-darken-4': !course.accentColor,
          'text-white': degreeStore.draggingCourseId === course.id
        }"
        density="compact"
        flat
        :icon="mdiDrag"
        v-bind="props"
      />
    </template>
    <v-list variant="flat">
      <v-list-item
        v-if="course.categoryId || course.ignore"
        id="assign-course-to-option-null"
        link-class="font-italic font-size-15 pl-3 text-body text-decoration-none"
        :value="null"
        @click="onSelect(null, false)"
      >
        -- Unassign --
      </v-list-item>
      <v-list-item
        v-if="!course.ignore"
        id="course-to-option-ignore"
        link-class="font-italic font-size-15 pl-3 text-body text-decoration-none"
        :value="null"
        @click="onSelect(null, true)"
      >
        -- {{ junkDrawerName }} --
      </v-list-item>
      <v-list-item
        v-for="option in options"
        :id="`assign-course-to-option-${option.id}`"
        :key="option.id"
        :disabled="option.disabled"
        :link-class="{
          'font-weight-700': !option.disabled && option.categoryType === 'Category',
          'font-weight-500': !option.disabled && option.categoryType === 'Subcategory',
          'font-weight-lighter': option.disabled,
          'font-size-15 pl-3': option.categoryType === 'Category',
          'font-size-14 pl-3': option.categoryType === 'Subcategory',
          'font-size-14 pl-4': isCourseRequirement(option) || isCampusRequirement(option),
          'text-body text-decoration-none': true
        }"
        :value="option"
        @click="onSelect(option, false)"
      >
        <span v-if="!option.disabled" class="sr-only">Move to </span>
        <span class="sr-only">{{ option.lineage }}</span>
        {{ option.name }}
        <span v-if="option.disabled" class="sr-only"> (disabled)</span>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script setup>
import {alertScreenReader} from '@/lib/utils'
import {assignCourse} from '@/api/degree'
import {categoryHasCourse, isCampusRequirement} from '@/lib/degree-progress'
import {mdiDrag} from '@mdi/js'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {computed, ref} from 'vue'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {cloneDeep, each, every, includes, isEmpty} from 'lodash'

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
const selectedOption = ref(null)

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
