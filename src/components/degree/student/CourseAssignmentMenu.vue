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
    <b-dropdown-group
      v-for="optionGroup in optionGroups"
      :id="`assign-course-${course.termId}-${course.sectionId}-option-group-${optionGroup.id}`"
      :key="optionGroup.id"
      :header="optionGroup.name"
    >
      <b-dropdown-item
        v-for="option in optionGroup.options"
        :id="`assign-course-${course.termId}-${course.sectionId}-option-${option.id}`"
        :key="option.id"
        link-class="font-size-16 text-decoration-none"
        :value="option"
        @click="onSelect(option)"
      >
        {{ option.name }}
      </b-dropdown-item>
    </b-dropdown-group>
  </b-dropdown>
</template>

<script>
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'

export default {
  name: 'CourseAssignmentMenu',
  mixins: [DegreeEditSession, Util],
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
    optionGroups: undefined,
    selectedOption: null
  }),
  created() {
    this.optionGroups = []
    this.$_.each(this.categories, category => {
      const optionGroup = {
        id: category.id,
        name: category.name,
        options: category.courses
      }
      this.$_.each(category.subcategories, subcategory => {
        if (subcategory.courses.length) {
          optionGroup.options.push(...subcategory.courses)
        }
      })
      if (optionGroup.options.length) {
        this.optionGroups.push(optionGroup)
      }
    })
  },
  methods: {
    onSelect(option) {
      this.$announcer.polite(`${option.name} selected for ${this.course.displayName}`)
      // TODO: Assign the course
      this.putFocusNextTick('XXX')
    }
  }
}
</script>
