<template>
  <b-dropdown
    :id="`assign-course-${course.id}-select`"
    v-model="selectedOption"
    :boundary="dropdownBoundary"
    :disabled="disableButtons || isSaving"
    :lazy="true"
    no-caret
    toggle-class="p-0 text-decoration-none"
    :toggle-text="`Assign ${course.name} to requirement`"
    variant="link"
  >
    <template #button-content>
      <font-awesome icon="grip-vertical" />
    </template>
    <b-dropdown-item
      v-for="option in options"
      :id="`assign-course-to-option-${option.id}`"
      :key="option.id"
      :disabled="!!option.fulfilledBy.length"
      :link-class="{
        'font-weight-lighter': option.fulfilledBy.length,
        'text-body text-decoration-none': true,
        'font-size-15 font-weight-bolder pl-3': option.categoryType === 'Category',
        'font-size-14 font-weight-500 pl-3': option.categoryType === 'Subcategory',
        'font-size-14 pl-4': option.categoryType === 'Course'
      }"
      :value="option"
      @click="onSelect(option)"
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
    },
    dropdownBoundary: {
      required: true,
      type: String
    },
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    isSaving: false,
    options: undefined,
    selectedOption: null
  }),
  created() {
    this.refresh()
  },
  methods: {
    onSelect(category) {
      this.$announcer.polite(`${category.name} selected for ${this.course.name}`)
      this.assignCourseToCategory({course: this.course, category}).then(() => {
        this.refresh()
      })
    },
    refresh() {
      this.options = []
      const push = option => {
        this.options.push(option)
      }
      this.$_.each(this.$_.cloneDeep(this.categories), category => {
        push(category)
        this.$_.each(category.courses, course => push(course))
        this.$_.each(category.subcategories, subcategory => {
          push(subcategory)
          this.$_.each(subcategory.courses, course => push(course))
        })
      })
    }
  }
}
</script>
