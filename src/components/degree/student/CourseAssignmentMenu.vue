<template>
  <v-menu
    :id="`assign-course-${course.id}-dropdown`"
    :disabled="degreeStore.disableButtons || isSaving"
    transition="slide-y-transition"
    @update:model-value="isOpen => isMenuOpen = isOpen"
  >
    <template #activator="{props: menuProps}">
      <button
        :id="`assign-course-${course.id}-btn`"
        :aria-label="`Assign ${course.name} to a Category or Course Requirement`"
        class="button-menu bg-transparent px-0 text-body-1"
        :class="{
          'accent-blue': course.accentColor === 'Blue',
          'accent-green': course.accentColor === 'Green',
          'accent-orange': course.accentColor === 'Orange',
          'accent-purple': course.accentColor === 'Purple',
          'accent-red': course.accentColor === 'Red',
          'text-primary': !degreeStore.disableButtons,
          'button-menu-active': isMenuOpen,
          'text-surface-variant': !course.accentColor,
          'text-white': degreeStore.draggingCourseId === course.id,
          'text-grey': degreeStore.disableButtons || isSaving
        }"
        v-bind="menuProps"
      >
        <v-icon :icon="mdiDrag" />
      </button>
    </template>
    <v-list :aria-label="`Choose a new location for ${course.name}`" class="overflow-x-hidden py-4" variant="flat">
      <v-list-item-action v-if="course.categoryId || course.ignore">
        <v-btn
          id="assign-course-to-option-null"
          class="font-italic d-flex justify-start"
          color="primary"
          density="comfortable"
          variant="text"
          width="100%"
          @click="onSelect(null, false)"
        >
          <span aria-hidden="true">-- </span>Unassign<span aria-hidden="true"> --</span>
        </v-btn>
      </v-list-item-action>
      <v-list-item-action v-if="!course.ignore">
        <v-btn
          id="course-to-option-ignore"
          class="font-italic d-flex justify-start"
          color="primary"
          density="comfortable"
          variant="text"
          width="100%"
          @click="onSelect(null, true)"
        >
          <span aria-hidden="true">-- </span>{{ junkDrawerName }}<span aria-hidden="true"> --</span>
        </v-btn>
      </v-list-item-action>
      <hr class="my-2">
      <v-list-item-action v-for="option in options" :key="option.id">
        <v-btn
          :id="`assign-course-to-option-${option.id}`"
          block
          class="d-flex justify-start v-btn-content-override"
          :class="{
            'font-size-16': option.categoryType === 'Category',
            'font-size-15 pl-4': option.categoryType === 'Subcategory',
            'font-size-13 pl-6': isCourseRequirement(option) || isCampusRequirement(option)
          }"
          color="primary"
          :disabled="option.disabled"
          variant="text"
          @click="onSelect(option, false)"
        >
          <span class="sr-only">{{ option.categoryType }}</span>
          <span class="truncate-with-ellipsis">{{ option.name }}</span>
          <span v-if="option.parent" class="sr-only">of {{ option.parent }}</span>
        </v-btn>
      </v-list-item-action>
    </v-list>
  </v-menu>
</template>

<script setup>
import {cloneDeep, each, every, includes, isEmpty} from 'lodash'
import {computed, ref} from 'vue'
import {mdiDrag} from '@mdi/js'
import {alertScreenReader} from '@/lib/utils'
import {assignCourse} from '@/api/degree'
import {categoryHasCourse, isCampusRequirement} from '@/lib/degree-progress'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/degree-edit-session-utils'
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

const isMenuOpen = ref(false)
const isSaving = ref(false)
const junkDrawerName = 'Other Coursework'

const options = computed(() => {
  const put = (option, parent) => {
    option.disabled = (isCourseRequirement(option) && !!option.courses.length)
      || (option.categoryType === 'Category' && !!option.subcategories.length)
      || categoryHasCourse(option, props.course)
    option.parent = parent ? `${parent.categoryType} ${parent.name}` : ''
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
      each(subcategory.courseRequirements, course => put(course, subcategory))
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
        alertScreenReader(`${props.course.name} assigned to "${category.name}"`)
      } else {
        alertScreenReader(`${props.course.name} moved to ${ignore ? props.junkDrawerName : 'Unassigned Courses'}`)
      }
      props.afterCourseAssignment(courseAssigned)
    })
  })
}
</script>

<style>
.v-btn-content-override .v-btn__content {
  width: 100%;
}
</style>

<style scoped>
.button-menu {
  --v-btn-height: 28px;
  border-radius: 100%;
  min-width: calc(var(--v-btn-height)) !important;
  width: calc(var(--v-btn-height)) !important;
}
</style>
