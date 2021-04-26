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
      <font-awesome icon="grip-vertical" />
    </template>
    <b-dropdown-item
      v-if="$_.size(course.categoryIds)"
      id="`assign-course-to-option-null`"
      link-class="font-size-15 font-weight-bolder pl-3 text-body text-decoration-none"
      :value="null"
      @click="onSelect(null)"
    >
      -- Unassign --
    </b-dropdown-item>
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
    student: {
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
      const options = []
      this.$_.each(this.$_.cloneDeep(this.categories), category => {
        options.push(category)
        this.$_.each(category.courses, course => options.push(course))
        this.$_.each(category.subcategories, subcategory => {
          options.push(subcategory)
          this.$_.each(subcategory.courses, course => options.push(course))
        })
      })
      return options
    }
  },
  methods: {
    onSelect(category) {
      if (category) {
        this.assignCourse({course: this.course, categoryId: category.id}).then(() => {
          this.$announcer.polite(`${category.name} selected for ${this.course.name}`)
        })
      } else {
        this.unassignCourse(this.course).then(() => {
          this.$announcer.polite('Course unassigned')
        })
      }
    }
  }
}
</script>
