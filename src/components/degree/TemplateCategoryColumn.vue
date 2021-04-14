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
    <div v-if="isAddingCategory">
      <EditCategory
        :after-cancel="onExitEditCategory"
        :after-save="onExitEditCategory"
        :position="position"
      />
    </div>
    <div
      v-for="category in $_.filter(categories, c => c.position === position && this.$_.isNil(c.parentCategoryId))"
      :key="category.id"
    >
      <Category
        v-if="category.id !== $_.get(categoryForEdit, 'id')"
        :category="category"
        :on-click-edit="edit"
        :position="position"
      />
      <div v-if="category.categoryType !== 'Category'" class="pl-2 pt-2">
        <span class="font-weight-500 has-error">Warning:</span> <span class="font-weight-500">"{{ category.name }}"</span>
        is a <span class="font-weight-500">{{ category.categoryType }}</span>, which is not allowed as a top-level
        category. Email <a :href="`mailto:${$config.supportEmailAddress}`" target="_blank">{{ $config.supportEmailAddress }}<span class="sr-only"> (new browser tab will open)</span></a>
        to report the problem.
      </div>
      <EditCategory
        v-if="category.id === $_.get(categoryForEdit, 'id')"
        :after-cancel="onExitEditCategory"
        :after-save="onExitEditCategory"
        :existing-category="category"
        :position="position"
      />
      <div v-if="$_.size(category.courses)" class="pl-2 py-2">
        <CoursesTable
          :courses="category.courses"
          :position="position"
        />
      </div>
      <div v-if="$_.size(category.subcategories)">
        <div v-for="subcategory in category.subcategories" :key="subcategory.id">
          <Category
            v-if="subcategory.id !== $_.get(categoryForEdit, 'id')"
            :category="subcategory"
            :position="position"
            :on-click-edit="edit"
          />
          <EditCategory
            v-if="subcategory.id === $_.get(categoryForEdit, 'id')"
            :after-cancel="onExitEditCategory"
            :after-save="onExitEditCategory"
            :existing-category="subcategory"
            :position="position"
          />
          <div v-if="$_.size(subcategory.courses)" class="pl-2 py-2">
            <CoursesTable
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
import Category from '@/components/degree/Category'
import CoursesTable from '@/components/degree/CoursesTable'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import EditCategory from '@/components/degree/EditCategory'
import Util from '@/mixins/Util'

export default {
  name: 'TemplateCategoryColumn',
  mixins: [DegreeEditSession, Util],
  components: {Category, CoursesTable, EditCategory},
  props: {
    position: {
      required: true,
      type: Number
    }
  },
  data: () => ({
    categoryForEdit: undefined,
    isAddingCategory: false
  }),
  methods: {
    add() {
      this.$announcer.polite('Add category')
      this.isAddingCategory = true
      this.setDisableButtons(true)
    },
    edit(category) {
      this.categoryForEdit = category
      this.setDisableButtons(true)
      this.$announcer.polite(`Edit ${category.categoryType} "${category.name}"`)
    },
    onExitEditCategory() {
      this.categoryForEdit = null
      this.isAddingCategory = false
      this.setDisableButtons(false)
    }
  }
}
</script>
