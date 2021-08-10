<template>
  <div>
    Hello World
  </div>
</template>

<script>
import DegreeEditSession from '@/mixins/DegreeEditSession'

export default {
  name: 'EditCourseRequirement',
  mixins: [DegreeEditSession],
  props: {
    afterCancel: {
      required: true,
      type: Function
    },
    afterSave: {
      required: true,
      type: Function
    },
    category: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    isRecommended: undefined,
    isSaving: false
  }),
  created() {
    this.isRecommended = this.category.isRecommended
    this.$putFocusNextTick(`category-${this.category.id}-recommended-checkbox`)
  },
  methods: {
    cancel() {
      this.isRecommended = undefined
      this.afterCancel()
    },
    onSubmit() {
      this.isSaving = true
      const done = () => {
        this.$announcer.polite('Course Requirement updated')
        this.isSaving = false
        this.afterSave()
      }
      this.updateCourseRequirement({
        categoryId: this.category.id,
        isRecommended: this.isRecommended
      }).then(done)
    }
  }
}
</script>
