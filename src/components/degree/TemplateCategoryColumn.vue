<template>
  <div>
    <div class="d-flex flex-row pb-3">
      <div class="pill degree-progress-pill px-2 no-wrap">Column {{ position }}</div>
      <b-btn
        v-if="$currentUser.canEditDegreeProgress"
        :id="`column-${position}-create-btn`"
        class="d-flex flex-row-reverse justify-content-end text-nowrap py-0"
        :disabled="disableButtons"
        variant="link"
        @click="add"
      >
        Add column {{ position }} requirement
        <font-awesome icon="plus" class="m-1" />
      </b-btn>
    </div>
    <AddDegreeCategory
      v-if="isAddingCategory"
      :after-cancel="afterCancelAddCategory"
      :after-create="afterCategoryCreate"
      :position="position"
    />
    <div
      v-for="parent in $_.filter(categories, c => c.position === position && this.$_.isNil(c.parentCategoryId))"
      :key="parent.id"
    >
      <DegreeTemplateCategory :category="parent" :position="position" />
    </div>
    <div
      v-if="!isAddingCategory && !$_.filter(categories, c => c.position === position).length"
      class="no-data-text pb-3 pl-1"
    >
      None
    </div>
  </div>
</template>

<script>
import AddDegreeCategory from '@/components/degree/AddDegreeCategory'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import DegreeTemplateCategory from '@/components/degree/DegreeTemplateCategory'
import Util from '@/mixins/Util'

export default {
  name: 'TemplateCategoryColumn',
  mixins: [DegreeEditSession, Util],
  components: {AddDegreeCategory, DegreeTemplateCategory},
  props: {
    position: {
      required: true,
      type: Number
    }
  },
  data: () => ({
    isAddingCategory: false
  }),
  methods: {
    add() {
      this.isAddingCategory = true
      this.setDisableButtons(true)
    },
    afterCancelAddCategory() {
      this.isAddingCategory = false
      this.setDisableButtons(false)
    },
    afterCategoryCreate() {
      this.isAddingCategory = false
    }
  }
}
</script>
