<template>
  <b-dropdown
    :id="`assign-course-${course.id}-dropdown`"
    v-model="selectedOption"
    :disabled="disableButtons || isSaving"
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
          'text-white': isUserDragging(course.id)
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
import {mdiDrag} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'
import {assignCourse} from '@/api/degree'
import {categoryHasCourse, isCampusRequirement} from '@/lib/degree-progress'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'

export default {
  name: 'CourseAssignmentMenu',
  mixins: [Context, DegreeEditSession, Util],
  props: {
    course: {
      required: true,
      type: Object
    },
    afterCourseAssignment: {
      default: () => {},
      required: false,
      type: Function
    }
  },
  data: () => ({
    isSaving: false,
    junkDrawerName: 'Other Coursework',
    selectedOption: null
  }),
  computed: {
    options() {
      const put = (option, parent, grandparent) => {
        option.disabled = (this.isCourseRequirement(option) && !!option.courses.length)
          || (option.categoryType === 'Category' && !!option.subcategories.length)
          || categoryHasCourse(option, this.course)
        option.lineage = grandparent ? `${grandparent.name} ${parent.name}` : (parent ? parent.name : '')
        if ((!option.disabled || !this.isCourseRequirement(option)) && !this.isCampusRequirements(option)) {
          options.push(option)
        }
      }
      const options = []
      this._each(this._cloneDeep(this.categories), category => {
        put(category)
        this._each(category.courseRequirements, courseRequirement => put(courseRequirement, category))
        this._each(category.subcategories, subcategory => {
          put(subcategory, category)
          this._each(subcategory.courseRequirements, course => put(course, subcategory, category))
        })
      })
      return options
    }
  },
  methods: {
    isCampusRequirement,
    isCampusRequirements(option) {
      return isCampusRequirement(option)
        || (!this._isEmpty(option.courseRequirements) && this._every(option.courseRequirements, isCampusRequirement))
    },
    isCourseRequirement(option) {
      return this._includes(['Course Requirement', 'Placeholder: Course Copy'], option.categoryType)
    },
    onSelect(category, ignore) {
      this.setDisableButtons(true)
      const categoryId = category && category.id
      assignCourse(this.course.id, categoryId, ignore).then(() => {
        refreshDegreeTemplate(this.templateId).then(courseAssigned => {
          this.setDisableButtons(false)
          if (category) {
            this.alertScreenReader(`${category.name} selected for ${this.course.name}`)
          } else {
            this.alertScreenReader(`Moved to ${ignore ? this.junkDrawerName : 'Unassigned'}`)
          }
          this.afterCourseAssignment(courseAssigned)
        })
      })
    }
  }
}
</script>
