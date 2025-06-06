<template>
  <div class="controls-container">
    <div
      v-if="isMovingCategory"
      class="d-flex align-center text-success font-size-14 font-weight-bold"
    >
      <v-progress-circular
        class="mr-2"
        indeterminate
        size="16"
        width="2"
      />
      Moving...
    </div>
    <v-btn-toggle
      v-if="!isMovingCategory"
      class="border-sm btn-control-position-y"
      color="primary"
      density="compact"
      :disabled="!canMoveUp && !canMoveDown"
      divided
      size="sm"
      variant="flat"
    >
      <v-btn
        :id="`decrease-position-y-category-${category.id}`"
        :disabled="!canMoveDown || degreeStore.disableButtons"
        :icon="mdiArrowDownBoldBoxOutline"
        :title="`Move ${category.categoryType} down`"
        @click="moveDown"
      />
      <v-btn
        :id="`increase-position-y-category-${category.id}`"
        color="primary"
        :disabled="!canMoveUp || degreeStore.disableButtons"
        :icon="mdiArrowUpBoldBoxOutline"
        :title="`Move ${category.categoryType} up`"
        @click="moveUp"
      />
    </v-btn-toggle>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {ref} from 'vue'
import {mdiArrowDownBoldBoxOutline, mdiArrowUpBoldBoxOutline} from '@mdi/js'
import type {Category} from '@/lib/types'
import {alertScreenReader} from '@/lib/utils'
import {moveCategoryDown, moveCategoryUp} from '@/api/degree'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/degree-edit-session-utils'
import {useDegreeStore} from '@/stores/degree-edit-session'

const props = defineProps({
  canMoveDown: {
    required: true,
    type: Boolean
  },
  canMoveUp: {
    required: false,
    type: Boolean
  },
  category: {
    required: true,
    type: Object as PropType<Category>
  }
})

const degreeStore = useDegreeStore()
const isMovingCategory = ref(false)

const moveDown = () => {
  isMovingCategory.value = true
  degreeStore.setDisableButtons(true)
  moveCategoryDown(props.category.id).then(() => {
    refreshDegreeTemplate(degreeStore.templateId).then(() => {
      degreeStore.setDisableButtons(false)
      isMovingCategory.value = false
      alertScreenReader(`"Category ${props.category.name}" moved down.`)
    })
  })
}

const moveUp = () => {
  isMovingCategory.value = true
  degreeStore.setDisableButtons(true)
  moveCategoryUp(props.category.id).then(() => {
    refreshDegreeTemplate(degreeStore.templateId).then(() => {
      degreeStore.setDisableButtons(false)
      isMovingCategory.value = false
      alertScreenReader(`"Category ${props.category.name}" moved down.`)
    })
  })
}
</script>

<style scoped>
.btn-control-position-y {
  color: rgb(var(--v-theme-primary));
  height: 28px;
}
.controls-container {
  height: 30px !important;
}
</style>
