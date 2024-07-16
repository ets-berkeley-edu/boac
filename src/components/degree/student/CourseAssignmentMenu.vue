<template>
  <b-dropdown
    :id="`assign-course-${course.id}-dropdown`"
    v-model="selectedOption"
    :disabled="degreeStore.disableButtons || isSaving"
    :lazy="true"
    no-caret
    toggle-class="p-0 text-decoration-none"
    variant="link"
  >
    <template #button-content>
      <span class="sr-only">{{ course.name }} category options</span>
      <v-icon
        class="font-size-16"
        :class="{
          'accent-color-blue': course.accentColor === 'Blue',
          'accent-color-green': course.accentColor === 'Green',
          'accent-color-orange': course.accentColor === 'Orange',
          'accent-color-purple': course.accentColor === 'Purple',
          'accent-color-red': course.accentColor === 'Red',
          'text-grey': !course.accentColor,
          'text-white': degreeStore.isUserDragging(course.id)
        }"
        :icon="mdiDrag"
      />
    </template>
    <b-dropdown-item
      v-if="course.categoryId || course.ignore"
      id="assign-course-to-option-null"
      link-class="font-italic font-size-15 pl-3 text-body text-decoration-none"
      :value="null"
      @click="onSelect(null, false)"
    >
      -- Unassign --
    </b-dropdown-item>
    <b-dropdown-item
      v-if="!course.ignore"
      id="course-to-option-ignore"
      link-class="font-italic font-size-15 pl-3 text-body text-decoration-none"
      :value="null"
      @click="onSelect(null, true)"
    >
      -- {{ junkDrawerName }} --
    </b-dropdown-item>
    <b-dropdown-item
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
    </b-dropdown-item>
  </b-dropdown>
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
  each(cloneDeep(this.categories), category => {
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
    refreshDegreeTemplate(this.templateId).then(courseAssigned => {
      this.setDisableButtons(false)
      if (category) {
        alertScreenReader(`${category.name} selected for ${props.course.name}`)
      } else {
        alertScreenReader(`Moved to ${ignore ? this.junkDrawerName : 'Unassigned'}`)
      }
      props.afterCourseAssignment(courseAssigned)
    })
  })
}
</script>
