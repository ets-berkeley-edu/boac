<template>
  <div>
    <div
      id="drop-zone-category"
      class="w-100"
      :class="{
        'border-b-sm border-e-sm border-t-sm': category.categoryType !== 'Subcategory' && !degreeStore.sid && canEdit,
        'drop-zone-container-category': category.categoryType === 'Category' && !printable,
        'drop-zone-container-subcategory': category.categoryType === 'Subcategory' && !size(category.subcategories) && !printable,
        'drop-zone-on': isDroppable() && degreeStore.draggingContext.target === category.id
      }"
      @dragend="onDrag($event, 'end')"
      @dragenter="onDrag($event, 'enter')"
      @dragleave="onDrag($event, 'leave')"
      @dragover="onDrag($event, 'over')"
      @dragstart="onDrag($event, 'start')"
      @drop="onDropCourse($event)"
    >
      <div class="align-center d-flex py-1">
        <div v-if="!printable" class="mr-2">
          <CategoryControlPositionY
            v-if="!degreeStore.sid"
            :can-move-down="canMoveDown"
            :can-move-up="canMoveUp"
            :category="category"
            :ux-position-x="uxPositionX"
          />
        </div>
        <h3
          v-if="category.categoryType === 'Category'"
          :id="`column-${uxPositionX}-category-${category.id}-header`"
          class="category-header text-medium-emphasis"
          :class="{'font-size-14': printable, 'font-size-16': !printable}"
        >
          {{ category.name }}
        </h3>
        <h4
          v-if="category.categoryType === 'Subcategory'"
          class="subcategory-header text-medium-emphasis"
          :class="{'font-size-12': printable, 'font-size-14': !printable}"
        >
          {{ category.name }}
        </h4>
        <div
          v-if="!degreeStore.sid && canEdit"
          class="align-center degree-check-action-buttons d-flex float-right mr-2 ms-auto"
        >
          <v-btn
            :id="`column-${uxPositionX}-edit-category-${category.id}-btn`"
            :aria-label="`Edit ${category.name}`"
            :class="{'text-primary': !degreeStore.disableButtons}"
            :color="degreeStore.disableButtons ? 'grey' : 'transparent'"
            density="compact"
            :disabled="degreeStore.disableButtons"
            flat
            :icon="mdiNoteEditOutline"
            size="small"
            variant="text"
            @click.prevent="edit"
          />
          <v-btn
            :id="`column-${uxPositionX}-delete-category-${category.id}-btn`"
            :aria-label="`Delete ${category.name}`"
            :class="{'text-primary': !degreeStore.disableButtons}"
            :color="degreeStore.disableButtons ? 'grey' : 'transparent'"
            density="compact"
            :disabled="degreeStore.disableButtons"
            flat
            :icon="mdiTrashCan"
            size="small"
            variant="text"
            @click="deleteDegreeCategory"
          />
        </div>
      </div>
      <div
        v-if="category.description && printable"
        :id="`column-${category.id}-category-header-description`"
        class="border-0 category-description font-size-12 py-1"
        v-html="category.description"
      />
      <div
        v-if="category.description && !printable"
        :id="`column-${category.id}-category-header-description`"
        v-linkified
        class="category-description pl-1 py-1"
        v-html="category.description"
      />
    </div>
    <AreYouSureModal
      v-model="isDeleting"
      button-label-confirm="Delete"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      :modal-header="`Delete ${category.categoryType}`"
    >
      Are you sure you want to delete <strong>&quot;{{ category.name }}&quot;</strong>?
    </AreYouSureModal>
  </div>
</template>

<script setup>
import {mdiNoteEditOutline, mdiTrashCan} from '@mdi/js'
import {computed, ref} from 'vue'
import {every, get, isEmpty, size} from 'lodash'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import CategoryControlPositionY from '@/components/degree/CategoryControlPositionY'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {categoryHasCourse, isCampusRequirement} from '@/lib/degree-progress'
import {deleteCategory, onDrop} from '@/stores/degree-edit-session/degree-edit-session-utils'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'

const props = defineProps({
  canMoveDown: {
    required: false,
    type: Boolean
  },
  canMoveUp: {
    required: false,
    type: Boolean
  },
  category: {
    required: true,
    type: Object
  },
  uxPositionX: {
    required: true,
    type: Number
  },
  onClickEdit: {
    default: () => {},
    required: false,
    type: Function
  },
  printable: {
    required: false,
    type: Boolean
  }
})

const contextStore = useContextStore()
const degreeStore = useDegreeStore()

const currentUser = contextStore.currentUser
const canEdit = currentUser.canEditDegreeProgress && !props.printable
const isCampusRequirements = computed(() => {
  return !isEmpty(props.category.courseRequirements) && every(props.category.courseRequirements, isCampusRequirement)
})
const isDeleting = ref(false)

const deleteCanceled = () => {
  isDeleting.value = false
  alertScreenReader('Canceled. Nothing deleted.')
  degreeStore.setDisableButtons(false)
  putFocusNextTick(`column-${props.uxPositionX}-delete-category-${props.category.id}-btn`)
}

const deleteConfirmed = () => {
  alertScreenReader(`Deleting ${props.category.categoryType}`)
  deleteCategory(props.category.id).then(() => {
    alertScreenReader(`Deleted "${props.category.name}" ${props.category.categoryType}.`)
    isDeleting.value = false
    degreeStore.setDisableButtons(false)
    putFocusNextTick(`column-${props.uxPositionX}-create-btn`)
  })
}

const deleteDegreeCategory = () => {
  degreeStore.setDisableButtons(true)
  isDeleting.value = true
}

const edit = () => {
  props.onClickEdit(props.category)
}

const isDroppable = () => {
  return props.category.id === degreeStore.draggingContext.target
    && !isCampusRequirements.value
    && !size(props.category.subcategories)
    && !categoryHasCourse(props.category, degreeStore.draggingContext.course)
}

const onDrag = (event, stage) => {
  switch (stage) {
  case 'end':
    degreeStore.setDraggingTarget(null)
    degreeStore.draggingContextReset()
    break
  case 'enter':
  case 'over':
    event.stopPropagation()
    event.preventDefault()
    degreeStore.setDraggingTarget(props.category.id)
    break
  case 'leave':
    if (get(event.target, 'id') === 'drop-zone-category') {
      degreeStore.setDraggingTarget(null)
    }
    break
  case 'exit':
  default:
    break
  }
}

const onDropCourse = event => {
  event.stopPropagation()
  event.preventDefault()
  if (isDroppable()) {
    onDrop(props.category, 'requirement')
  }
  degreeStore.setDraggingTarget(null)
  return false
}
</script>

<style scoped>
.category-description {
  white-space: pre-line;
}
.category-header {
  font-weight: bold;
  margin-bottom: 0;
  padding: 0;
}
.drop-zone-container-category {
  background-color: rgb(var(--v-theme-surface-light));
  border-left: 3px solid rgb(var(--v-theme-primary));
  padding: 0 0 0 0.5em;
  margin: 0.2em 0 0.2em 0;
}
.drop-zone-container-subcategory {
  background-color: rgb(var(--v-theme-light-grey));
  border-left: 3px solid rgb(var(--v-theme-secondary));
  padding: 0 0 0 0.5em;
  margin: 0.2em 0 0.2em 0;
}
.subcategory-header {
  font-weight: bold;
  margin-bottom: 0;
  padding: 0;
}
</style>
