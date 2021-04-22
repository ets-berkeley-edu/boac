<template>
  <b-dropdown
    :id="`assign-course-${course.termId}-${course.sectionId}-select`"
    v-model="selectedOption"
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
      :link-class="{
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
import {assignCourse} from '@/api/degree'

export default {
  name: 'CourseAssignmentMenu',
  mixins: [DegreeEditSession],
  props: {
    afterSelect: {
      default: () => {},
      required: false,
      type: Function
    },
    course: {
      required: true,
      type: Object
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
    this.options = []
    this.$_.each(this.$_.cloneDeep(this.categories), category => {
      this.options.push(category)
      this.$_.each([category.courses, category.subcategories], group => {
        this.$_.each(group, item => {
          this.options.push(item)
        })
      })
    })
  },
  methods: {
    onSelect(option) {
      this.$announcer.polite(`${option.name} selected for ${this.course.displayName}`)
      assignCourse(
        option.id,
        this.course.sectionId,
        this.course.sid,
        this.course.termId
      ).then(data => {
        this.afterSelect(data)
      })
    }
  }
}
</script>
