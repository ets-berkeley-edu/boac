<template>
  <div :id="`category-column-${uxPositionX}`">
    <div v-if="!degreeStore.sid" class="align-center d-flex flex-wrap justify-space-between">
      <v-chip
        class="font-size-13 text-no-wrap mb-1 mr-1 px-2 text-uppercase column-label"
        color="grey"
        density="compact"
        label
        variant="flat"
      >
        Column {{ uxPositionX }}
      </v-chip>
      <v-btn
        v-if="currentUser.canEditDegreeProgress"
        :id="`column-${uxPositionX}-create-btn`"
        :append-icon="mdiPlus"
        class="mb-1 ml-auto text-body-2"
        color="primary"
        density="comfortable"
        :disabled="degreeStore.disableButtons"
        :text="`Add column ${uxPositionX} requirement`"
        slim
        variant="text"
        @click="add"
      />
    </div>
    <div v-if="isAddingCategory" class="pb-6 pt-3">
      <EditCategory
        :after-cancel="onExitEditCategory"
        :after-save="onExitEditCategory"
        :ux-position-x="uxPositionX"
      />
    </div>
    <div
      v-for="(category, index) in _filter(degreeStore.categories, c => c.uxPositionX === uxPositionX && isNil(c.parentCategoryId))"
      :id="`column-${uxPositionX}-category-${category.id}`"
      :key="category.id"
      :aria-labelledby="`column-${uxPositionX}-category-${category.id}-header`"
      :class="{'mt-3': index === 0, 'mt-6': index > 0}"
      role="region"
    >
      <Category
        v-if="category.id !== get(categoryForEdit, 'id')"
        :key="`cat-${category.id}`"
        :category="category"
        :on-click-edit="edit"
        :ux-position-x="uxPositionX"
      />
      <v-alert
        v-if="category.categoryType !== 'Category'"
        aria-live="polite"
        class="text-body-2"
        density="compact"
        type="error"
        :icon="false"
        variant="tonal"
      >
        <span class="font-weight-600 text-error">Warning:</span> <span class="font-weight-500">"{{ category.name }}"</span>
        is a <span class="font-weight-500">{{ category.categoryType }}</span>, which is not allowed as a top-level
        category. <a :href="`mailto:${config.supportEmailAddress}`" target="_blank">Email {{ config.supportEmailAddress }}<span class="sr-only"> (opens in new window)</span></a>
        to report the problem.
      </v-alert>
      <EditCategory
        v-if="category.id === get(categoryForEdit, 'id')"
        :after-cancel="onExitEditCategory"
        :after-save="onExitEditCategory"
        :existing-category="category"
        :ux-position-x="uxPositionX"
      />
      <div v-if="!category.subcategories.length" class="mt-4">
        <CoursesTable
          :id="`column-${uxPositionX}-category-${category.id}-courses`"
          :items="getItemsForCoursesTable(category)"
          :parent-category="category"
          :ux-position-x="uxPositionX"
        />
      </div>
      <div v-if="category.subcategories.length">
        <div
          v-for="subcategory in category.subcategories"
          :id="`column-${uxPositionX}-subcategory-${subcategory.id}`"
          :key="subcategory.id"
          class="mt-6"
        >
          <Category
            v-if="subcategory.id !== get(categoryForEdit, 'id')"
            :key="`cat-${subcategory.id}`"
            :category="subcategory"
            class="w-100"
            :on-click-edit="edit"
            :ux-position-x="uxPositionX"
          />
          <EditCategory
            v-if="subcategory.id === get(categoryForEdit, 'id')"
            :after-cancel="onExitEditCategory"
            :after-save="onExitEditCategory"
            :existing-category="subcategory"
            :ux-position-x="uxPositionX"
          />
          <div class="mt-3">
            <CoursesTable
              :id="`column-${uxPositionX}-subcategory-${subcategory.id}-courses`"
              :items="getItemsForCoursesTable(subcategory)"
              :parent-category="subcategory"
              :ux-position-x="uxPositionX"
            />
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="!degreeStore.sid && !isAddingCategory && !_filter(degreeStore.categories, c => c.uxPositionX === uxPositionX).length"
      class="no-data-text pb-3"
    >
      No <span class="sr-only">Column {{ uxPositionX }}&nbsp;</span>requirements
    </div>
  </div>
</template>

<script setup>
import {mdiPlus} from '@mdi/js'
import {ref} from 'vue'
import {filter as _filter, get, isNil} from 'lodash'
import Category from '@/components/degree/Category'
import CoursesTable from '@/components/degree/CoursesTable'
import EditCategory from '@/components/degree/EditCategory'
import {getItemsForCoursesTable} from '@/lib/degree-progress'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'

const contextStore = useContextStore()
const degreeStore = useDegreeStore()

const props = defineProps({
  uxPositionX: {
    required: true,
    type: Number
  }
})

const categoryForEdit = ref(undefined)
const config = contextStore.config
const currentUser = contextStore.currentUser
const isAddingCategory = ref(false)

const add = () => {
  isAddingCategory.value = true
  degreeStore.setDisableButtons(true)
}

const edit = category => {
  categoryForEdit.value = category
  degreeStore.setDisableButtons(true)
  putFocusNextTick(`column-${props.uxPositionX}-name-input`)
}

const onExitEditCategory = () => {
  const putFocus = categoryForEdit.value ? `column-${props.uxPositionX}-edit-category-${categoryForEdit.value.id}-btn` : `column-${props.uxPositionX}-create-btn`
  categoryForEdit.value = null
  isAddingCategory.value = false
  degreeStore.setDisableButtons(false)
  putFocusNextTick(putFocus)
}
</script>

<style scoped>
.column-label {
  min-width: 5.2rem !important;
}
</style>
