<template>
  <div>
    <div class="d-flex flex-row pb-3">
      <div class="pill degree-progress-pill px-2">Column {{ position }}</div>
      <b-btn
        :id="`column-${position}-create-link`"
        class="d-flex flex-row-reverse justify-content-end text-nowrap py-0"
        variant="link"
      >
        Add column {{ position }} requirement
        <font-awesome icon="plus" class="m-1" />
      </b-btn>
    </div>
    <div v-if="!categoriesPerPosition.length" class="no-data-text pb-3">
      No column {{ position }} requirements
    </div>
  </div>
</template>

<script>
import DegreeEditSession from '@/mixins/DegreeEditSession'

export default {
  name: 'TemplateCategoryColumn',
  mixins: [DegreeEditSession],
  props: {
    position: {
      required: true,
      type: Number
    }
  },
  computed: {
    categoriesPerPosition() {
      return this.$_.filter(this.categories, c => {
        return c.position === this.position && this.$_.isNil(c.parentCategoryId)
      })
    }
  }
}
</script>
