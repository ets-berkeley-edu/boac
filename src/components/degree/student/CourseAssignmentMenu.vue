<template>
  <b-dropdown
    :id="`assign-course-${course.id}-select`"
    v-model="selectedOption"
    :disabled="disableButtons || isSaving"
    :lazy="true"
    no-caret
    toggle-class="p-0 text-decoration-none"
    :toggle-text="`Assign ${course.name} to requirement`"
    variant="link"
  >
    <template #button-content>
      <font-awesome
        class="faint-text font-size-16"
        :class="{'text-white': isUserDragging(course.id)}"
        icon="grip-vertical"
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
      -- Junk Drawer --
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
        'font-size-14 pl-4': option.categoryType === 'Course Requirement',
        'text-body text-decoration-none': true
      }"
      :value="option"
      @click="onSelect(option, false)"
    >
      {{ option.name }}
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
    }
  },
  data: () => ({
    isSaving: false,
    selectedOption: null
  }),
  computed: {
    options() {
      const put = option => {
        option.disabled = (option.categoryType === 'Course Requirement' && !!option.courses.length)
          || (option.categoryType === 'Category' && !!option.subcategories.length)
          || this.categoryHasCourse(option, this.course)
        options.push(option)
      }
      const options = []
      this.$_.each(this.$_.cloneDeep(this.categories), category => {
        put(category)
        this.$_.each(category.courseRequirements, courseRequirement => put(courseRequirement))
        this.$_.each(category.subcategories, subcategory => {
          put(subcategory)
          this.$_.each(subcategory.courseRequirements, course => put(course))
        })
      })
      return options
    }
  },
  methods: {
    onSelect(category, ignore) {
      this.setDisableButtons(true)
      this.assignCourseToCategory({course: this.course, category, ignore}).then(() => {
        this.setDisableButtons(false)
        this.$announcer.polite(category ? `${category.name} selected for ${this.course.name}` : 'Course unassigned')
      })
    }
  }
}
</script>
