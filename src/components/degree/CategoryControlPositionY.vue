<template>
  <div>
    <v-btn-toggle
      class="border-sm btn-control-position-y"
      color="primary"
      density="compact"
      divided
      mandatory
      variant="flat"
    >
      <v-btn
        v-if="canMoveUp"
        :id="`increase-position-y-category-${category.id}`"
        color="primary"
        density="compact"
        elevation="0"
        :icon="mdiMenuUp"
        :title="`Move ${category.categoryType} up`"
        @click="moveUp"
      />
      <v-btn
        v-if="canMoveDown"
        :id="`decrease-position-y-category-${category.id}`"
        density="compact"
        elevation="0"
        :icon="mdiMenuDown"
        :title="`Move ${category.categoryType} down`"
        @click="moveDown"
      />
    </v-btn-toggle>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {computed} from 'vue'
import {filter as _filter, find, isNil, map, max, min, remove} from 'lodash'
import {mdiMenuDown, mdiMenuUp} from '@mdi/js'
import type {Category} from '@/lib/types'
import {useDegreeStore} from '@/stores/degree-edit-session'
import {moveCategoryDown, moveCategoryUp} from '@/api/degree'

const props = defineProps({
  category: {
    required: true,
    type: Object as PropType<Category>
  }
})

const degreeStore = useDegreeStore()

const canMoveDown = computed(() => {
  const maxUxPositionY = max(map(siblingCategories.value, 'uxPositionY'))
  return !isNil(maxUxPositionY) && props.category.uxPositionY < maxUxPositionY
})

const canMoveUp = computed(() => {
  const minUxPositionY = min(map(siblingCategories.value, 'uxPositionY'))
  return !isNil(minUxPositionY) && props.category.uxPositionY > minUxPositionY
})

const siblingCategories = computed(() => {
  let siblings: Category[]
  if (props.category.parentCategoryId) {
    const parent = find(degreeStore.categories, ['id', props.category.parentCategoryId])
    siblings = parent.subcategories
  } else {
    siblings = _filter(degreeStore.categories, c => c.uxPositionX === props.category.uxPositionX && isNil(c.parentCategoryId))
  }
  return remove(siblings,s => s.id !== props.category.id)
})

const moveDown = () => {
  moveCategoryDown(props.category.id).then(() => {
    // eslint-disable-next-line no-console
    console.log('Category is down.')
  })
}

const moveUp = () => {
  moveCategoryUp(props.category.id).then(() => {
    // eslint-disable-next-line no-console
    console.log('Category is up!')
  })
}
</script>

<style scoped>
.btn-control-position-y {
  border-color: rgb(var(--v-theme-primary)) !important;
  color: rgb(var(--v-theme-primary));
  height: 28px;
}
</style>
