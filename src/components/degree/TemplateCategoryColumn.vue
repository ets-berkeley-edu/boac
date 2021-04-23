<template>
  <div :id="`category-column-${position}`">
    <div v-if="!student" class="d-flex justify-content-between pb-3">
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
        :student="student"
      />
      <div v-if="category.categoryType !== 'Category'" class="pl-1 pt-2">
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
      <div v-if="$_.size(category.fulfilledBy)" class="pl-1 py-2">
        <CoursesTable
          :id="`column-${position}-category-${category.id}-fulfilled-by`"
          :courses="category.fulfilledBy"
          :position="position"
          :student="student"
        />
      </div>
      <div v-if="$_.size(category.courses)" class="pl-1 py-2">
        <CoursesTable
          :id="`column-${position}-category-${category.id}-courses`"
          :courses="category.courses"
          :position="position"
          :student="student"
        />
      </div>
      <div v-if="$_.size(category.subcategories)">
        <div
          v-for="subcategory in category.subcategories"
          :id="`column-${position}-category-${category.id}-subcategories`"
          :key="subcategory.id"
        >
          <Category
            v-if="subcategory.id !== $_.get(categoryForEdit, 'id')"
            :category="subcategory"
            :on-click-edit="edit"
            :position="position"
            :student="student"
          />
          <EditCategory
            v-if="subcategory.id === $_.get(categoryForEdit, 'id')"
            :after-cancel="onExitEditCategory"
            :after-save="onExitEditCategory"
            :existing-category="subcategory"
            :position="position"
          />
          <div v-if="$_.size(subcategory.fulfilledBy)" class="pl-1 py-2">
            <CoursesTable
              :id="`column-${position}-subcategory-${subcategory.id}-fulfilled-by`"
              :courses="subcategory.fulfilledBy"
              :position="position"
              :student="student"
            />
          </div>
          <div v-if="$_.size(subcategory.courses)" class="pl-1 py-2">
            <CoursesTable
              :id="`column-${position}-subcategory-${subcategory.id}-courses`"
              :courses="subcategory.courses"
              :position="position"
              :student="student"
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
    },
    student: {
      default: undefined,
      required: false,
      type: Object
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
