<template>
  <div :id="`category-column-${position}`">
    <div v-if="!sid" class="d-flex justify-content-between pb-3">
      <div class="pill bg-grey no-wrap px-2 text-uppercase text-white">Column {{ position }}</div>
      <b-btn
        v-if="$currentUser.canEditDegreeProgress"
        :id="`column-${position}-create-btn`"
        class="p-0"
        :disabled="disableButtons"
        variant="link"
        @click="add"
      >
        <div class="align-items-center d-flex justify-content-between">
          <div class="pr-2 text-nowrap">
            Add column {{ position }} requirement
          </div>
          <div>
            <font-awesome icon="plus" />
          </div>
        </div>
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
      v-for="category in $_.filter(categories, c => c.position === position && $_.isNil(c.parentCategoryId))"
      :id="`column-${position}-category-${category.id}`"
      :key="category.id"
    >
      <Category
        v-if="category.id !== $_.get(categoryForEdit, 'id')"
        :category="category"
        :on-click-edit="edit"
        :position="position"
      />
      <div v-if="category.categoryType !== 'Category'" class="pl-1">
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
      <div v-if="!category.subcategories.length" class="py-1">
        <CoursesTable
          :id="`column-${position}-category-${category.id}-courses`"
          :items="getItemsForCoursesTable(category)"
          :parent-category="category"
          :position="position"
        />
      </div>
      <div v-if="category.subcategories.length" class="pt-1">
        <div
          v-for="subcategory in category.subcategories"
          :id="`column-${position}-subcategory-${subcategory.id}`"
          :key="subcategory.id"
        >
          <Category
            v-if="subcategory.id !== $_.get(categoryForEdit, 'id')"
            :category="subcategory"
            :on-click-edit="edit"
            :position="position"
          />
          <EditCategory
            v-if="subcategory.id === $_.get(categoryForEdit, 'id')"
            :after-cancel="onExitEditCategory"
            :after-save="onExitEditCategory"
            :existing-category="subcategory"
            :position="position"
          />
          <div class="py-1">
            <CoursesTable
              :id="`column-${position}-subcategory-${subcategory.id}-courses`"
              :items="getItemsForCoursesTable(subcategory)"
              :parent-category="subcategory"
              :position="position"
            />
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="!isAddingCategory && !$_.filter(categories, c => c.position === position).length"
      class="no-data-text pb-3"
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
      this.$putFocusNextTick(`column-${this.position}-name-input`)
    },
    onExitEditCategory() {
      const putFocus = this.categoryForEdit ? `column-${this.position}-edit-category-${this.categoryForEdit.id}-btn` : `column-${this.position}-create-btn`
      this.categoryForEdit = null
      this.isAddingCategory = false
      this.setDisableButtons(false)
      this.$putFocusNextTick(putFocus)
    }
  }
}
</script>
