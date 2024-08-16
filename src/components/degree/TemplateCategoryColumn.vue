<template>
  <div :id="`category-column-${position}`">
    <div v-if="!degreeStore.sid" class="align-center d-flex justify-space-between pb-3">
      <div class="pill bg-grey text-no-wrap px-2 text-uppercase text-white">Column {{ position }}</div>
      <v-btn
        v-if="currentUser.canEditDegreeProgress"
        :id="`column-${position}-create-btn`"
        :append-icon="mdiPlus"
        :disabled="degreeStore.disableButtons"
        class="text-body-2"
        color="primary"
        :text="`Add column ${position} requirement`"
        variant="text"
        @click="add"
      />
    </div>
    <div v-if="isAddingCategory" class="pb-6 pt-3">
      <EditCategory
        :after-cancel="onExitEditCategory"
        :after-save="onExitEditCategory"
        :position="position"
      />
    </div>
    <div
      v-for="category in _filter(degreeStore.categories, c => c.position === position && isNil(c.parentCategoryId))"
      :id="`column-${position}-category-${category.id}`"
      :key="category.id"
    >
      <Category
        v-if="category.id !== get(categoryForEdit, 'id')"
        :category="category"
        :on-click-edit="edit"
        :position="position"
      />
      <div v-if="category.categoryType !== 'Category'" class="pl-1">
        <span class="font-weight-500 text-error">Warning:</span> <span class="font-weight-500">"{{ category.name }}"</span>
        is a <span class="font-weight-500">{{ category.categoryType }}</span>, which is not allowed as a top-level
        category. Email <a :href="`mailto:${config.supportEmailAddress}`" target="_blank">{{ config.supportEmailAddress }}<span class="sr-only"> (new browser tab will open)</span></a>
        to report the problem.
      </div>
      <EditCategory
        v-if="category.id === get(categoryForEdit, 'id')"
        :after-cancel="onExitEditCategory"
        :after-save="onExitEditCategory"
        :existing-category="category"
        :position="position"
      />
      <div v-if="!category.subcategories.length" class="mt-4">
        <CoursesTable
          :id="`column-${position}-category-${category.id}-courses`"
          :items="getItemsForCoursesTable(category)"
          :parent-category="category"
          :position="position"
        />
      </div>
      <div v-if="category.subcategories.length" class="mt-2">
        <div
          v-for="subcategory in category.subcategories"
          :id="`column-${position}-subcategory-${subcategory.id}`"
          :key="subcategory.id"
        >
          <Category
            v-if="subcategory.id !== get(categoryForEdit, 'id')"
            :category="subcategory"
            :on-click-edit="edit"
            :position="position"
          />
          <EditCategory
            v-if="subcategory.id === get(categoryForEdit, 'id')"
            :after-cancel="onExitEditCategory"
            :after-save="onExitEditCategory"
            :existing-category="subcategory"
            :position="position"
          />
          <div class="mt-2">
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
      v-if="!degreeStore.sid && !isAddingCategory && !_filter(degreeStore.categories, c => c.position === position).length"
      class="no-data-text pb-3"
    >
      None
    </div>
  </div>
</template>

<script setup>
import Category from '@/components/degree/Category'
import CoursesTable from '@/components/degree/CoursesTable'
import EditCategory from '@/components/degree/EditCategory'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {getItemsForCoursesTable} from '@/lib/degree-progress'
import {mdiPlus} from '@mdi/js'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {ref} from 'vue'
import {filter as _filter, get, isNil} from 'lodash'

const contextStore = useContextStore()
const degreeStore = useDegreeStore()

const props = defineProps({
  position: {
    required: true,
    type: Number
  }
})

const categoryForEdit = ref(undefined)
const config = contextStore.config
const currentUser = contextStore.currentUser
const isAddingCategory = ref(false)

const add = () => {
  alertScreenReader('Add category')
  isAddingCategory.value = true
  degreeStore.setDisableButtons(true)
}

const edit = category => {
  categoryForEdit.value = category
  degreeStore.setDisableButtons(true)
  alertScreenReader(`Edit ${category.categoryType} "${category.name}"`)
  putFocusNextTick(`column-${props.position}-name-input`)
}

const onExitEditCategory = () => {
  const putFocus = categoryForEdit.value ? `column-${props.position}-edit-category-${categoryForEdit.value.id}-btn` : `column-${props.position}-create-btn`
  categoryForEdit.value = null
  isAddingCategory.value = false
  degreeStore.setDisableButtons(false)
  putFocusNextTick(putFocus)
}
</script>
