<template>
  <div class="controls-container">
    <v-btn-group
      class="btn-control-position-y"
      :color="isMovingDown || isMovingUp ? 'green' : 'primary'"
      density="compact"
      :disabled="!canMoveUp && !canMoveDown"
      divided
      size="sm"
      variant="outlined"
    >
      <v-btn
        :id="`decrease-position-y-category-${category.id}`"
        :disabled="!canMoveDown || degreeStore.disableButtons"
        :icon="isMovingDown ? mdiProgressCheck : mdiArrowDownBoldBoxOutline"
        :title="`Move ${category.categoryType} down`"
        @click="moveDown"
      />
      <v-btn
        :id="`increase-position-y-category-${category.id}`"
        :disabled="!canMoveUp || degreeStore.disableButtons"
        :icon="isMovingUp ? mdiProgressCheck : mdiArrowUpBoldBoxOutline"
        :title="`Move ${category.categoryType} up`"
        @click="moveUp"
      />
    </v-btn-group>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {ref} from 'vue'
import {mdiArrowDownBoldBoxOutline, mdiArrowUpBoldBoxOutline, mdiProgressCheck} from '@mdi/js'
import type {Category} from '@/lib/types'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
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
const isMovingDown = ref(false)
const isMovingUp = ref(false)

const moveDown = () => {
  isMovingDown.value = true
  degreeStore.setDisableButtons(true)
  moveCategoryDown(props.category.id).then(() => {
    refreshDegreeTemplate(degreeStore.templateId).then(() => {
      degreeStore.setDisableButtons(false)
      isMovingDown.value = false
      alertScreenReader(`${props.category.categoryType} "${props.category.name}" moved down.`)
      putFocusNextTick(`increase-position-y-category-${props.category.id}`)
    })
  })
}

const moveUp = () => {
  isMovingUp.value = true
  degreeStore.setDisableButtons(true)
  moveCategoryUp(props.category.id).then(() => {
    refreshDegreeTemplate(degreeStore.templateId).then(() => {
      degreeStore.setDisableButtons(false)
      isMovingUp.value = false
      alertScreenReader(`${props.category.categoryType} "${props.category.name}" moved up.`)
      putFocusNextTick(`decrease-position-y-category-${props.category.id}`)
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
  width: 58px !important;
}
</style>
