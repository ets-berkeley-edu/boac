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
      <font-awesome
        class="font-size-16"
        :class="{
          'accent-color-blue': course.accentColor === 'Blue',
          'accent-color-green': course.accentColor === 'Green',
          'accent-color-orange': course.accentColor === 'Orange',
          'accent-color-purple': course.accentColor === 'Purple',
          'accent-color-red': course.accentColor === 'Red',
          'faint-text': !course.accentColor,
          'text-white': isUserDragging(course.id)
        }"
        icon="grip-vertical"
      />
    </template>
    <b-dropdown-item
      v-if="!course.isCopy && (course.categoryId || course.ignore)"
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
        'font-weight-bolder': !option.disabled && option.categoryType === 'Category',
        'font-weight-500': !option.disabled && option.categoryType === 'Subcategory',
        'font-weight-lighter': option.disabled,
        'font-size-15 pl-3': option.categoryType === 'Category',
        'font-size-14 pl-3': option.categoryType === 'Subcategory',
        'font-size-14 pl-4': isCourseRequirement(option),
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

<script>
import DegreeEditSession from '@/mixins/DegreeEditSession'

export default {
  name: 'CourseAssignmentMenu',
  mixins: [DegreeEditSession],
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
    junkDrawerName: 'Free Electives',
    selectedOption: null
  }),
  computed: {
    options() {
      const put = (option, parent, grandparent) => {
        option.disabled = (this.isCourseRequirement(option) && !!option.courses.length)
          || (option.categoryType === 'Category' && !!option.subcategories.length)
          || this.categoryHasCourse(option, this.course)
        option.lineage = grandparent ? `${grandparent.name} ${parent.name}` : (parent ? parent.name : '')
        if (!option.disabled || !this.isCourseRequirement(option)) {
          options.push(option)
        }
      }
      const options = []
      this.$_.each(this.$_.cloneDeep(this.categories), category => {
        put(category)
        this.$_.each(category.courseRequirements, courseRequirement => put(courseRequirement, category))
        this.$_.each(category.subcategories, subcategory => {
          put(subcategory, category)
          this.$_.each(subcategory.courseRequirements, course => put(course, subcategory, category))
        })
      })
      return options
    }
  },
  methods: {
    isCourseRequirement(option) {
      return this.$_.includes(['Course Requirement', 'Placeholder: Course Copy'], option.categoryType)
    },
    onSelect(category, ignore) {
      this.setDisableButtons(true)
      this.assignCourseToCategory({course: this.course, category, ignore}).then(courseAssigned => {
        this.setDisableButtons(false)
        if (category) {
          this.$announcer.polite(`${category.name} selected for ${this.course.name}`)
        } else {
          this.$announcer.polite(`Moved to ${ignore ? this.junkDrawerName : 'Unassigned'}`)
        }
        this.afterCourseAssignment(courseAssigned)
      })
    }
  }
}
</script>
