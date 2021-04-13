<template>
  <div>
    <div class="d-flex flex-row mt-2 pb-3">
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
      v-for="category in $_.filter(categories, c => c.position === position && this.$_.isNil(c.parentCategoryId))"
      :key="category.id"
    >
      <DegreeTemplateCategory :category="category" :position="position" />

      <div v-if="category.courses.length" class="pl-2 py-2">
        <DegreeTemplateCoursesTable
          :courses="category.courses"
          :position="position"
        />
      </div>
      <div v-if="category.subcategories.length">
        <div v-for="subcategory in category.subcategories" :key="subcategory.id">
          <DegreeTemplateCategory :category="subcategory" :position="position" />
          <div v-if="subcategory.courses.length" class="pl-2 py-2">
            <DegreeTemplateCoursesTable
              :courses="subcategory.courses"
              :position="position"
            />
          </div>
        </div>
      </div>
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
import DegreeTemplateCoursesTable from '@/components/degree/DegreeTemplateCoursesTable'
import Util from '@/mixins/Util'

export default {
  name: 'TemplateCategoryColumn',
  mixins: [DegreeEditSession, Util],
  components: {AddDegreeCategory, DegreeTemplateCategory, DegreeTemplateCoursesTable},
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
      this.$announcer.polite('Add category')
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
