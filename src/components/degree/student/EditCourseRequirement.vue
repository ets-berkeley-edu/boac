<template>
  <div class="pb-3 pl-4 pt-2">
    <div class="mb-2">
      <label for="recommended-course-checkbox" class="font-size-14 font-weight-bolder mb-1">Course Indicator</label>
      <b-form-checkbox
        id="recommended-course-checkbox"
        v-model="isRecommended"
      >
        Recommended course
      </b-form-checkbox>
    </div>
    <div class="d-flex">
      <div class="pr-2">
        <b-btn
          id="update-requirement-btn"
          class="btn-primary-color-override"
          :disabled="isSaving"
          size="sm"
          variant="primary"
          @click="onSubmit"
        >
          <span v-if="isSaving">
            <font-awesome class="mr-1" icon="spinner" spin /> Saving
          </span>
          <span v-if="!isSaving">Save</span>
        </b-btn>
      </div>
      <div>
        <b-btn
          id="cancel-edit-requirement-btn"
          class="btn-primary-color-override btn-primary-color-outline-override"
          :disabled="isSaving"
          size="sm"
          variant="outline-primary"
          @click="cancel"
        >
          Cancel
        </b-btn>
      </div>
    </div>
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
