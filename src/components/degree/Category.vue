<template>
  <div>
    <div
      id="drop-zone-category"
      class="w-100"
      :class="{
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
      <div class="align-center d-flex justify-space-between w-100">
        <h3
          v-if="category.categoryType === 'Category'"
          :id="`column-${position}-category-${category.id}-header`"
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
        <div v-if="!degreeStore.sid && canEdit" class="degree-check-action-buttons align-center d-flex text-no-wrap">
          <v-btn
            :id="`column-${position}-edit-category-${category.id}-btn`"
            :aria-label="`Edit ${category.name}`"
            :class="{'text-primary': !degreeStore.disableButtons}"
            class="action-btn"
            density="compact"
            :disabled="degreeStore.disableButtons"
            flat
            :icon="mdiNoteEditOutline"
            size="small"
            @click.prevent="edit"
          />
          <v-btn
            :id="`column-${position}-delete-category-${category.id}-btn`"
            :aria-label="`Delete ${category.name}`"
            :class="{'text-primary': !degreeStore.disableButtons}"
            class="action-btn"
            density="compact"
            :disabled="degreeStore.disableButtons"
            flat
            :icon="mdiTrashCan"
            size="small"
            @click="deleteDegreeCategory"
          />
        </div>
      </div>
      <div
        v-if="category.description && printable"
        :id="`column-${category.id}-category-header-description`"
        class="category-description py-1"
        :class="{'': printable, 'pl-1': !printable}"
      >
        <span v-if="printable" class="border-0" v-html="category.description" />
      </div>
      <div
        v-if="category.description"
        :id="`column-${category.id}-category-header-description`"
        class="category-description py-1"
        :class="{'font-size-12': printable, 'pl-1': !printable}"
      >
        <span v-if="printable" class="border-0" v-html="category.description" />
        <span v-if="!printable" v-linkified v-html="category.description" />
      </div>
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
import AreYouSureModal from '@/components/util/AreYouSureModal'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {categoryHasCourse, isCampusRequirement} from '@/lib/degree-progress'
import {deleteCategory, onDrop} from '@/stores/degree-edit-session/utils'
import {mdiNoteEditOutline, mdiTrashCan} from '@mdi/js'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {computed, ref} from 'vue'
import {every, get, isEmpty, size} from 'lodash'

const props = defineProps({
  category: {
    required: true,
    type: Object
  },
  position: {
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
  putFocusNextTick(`column-${props.position}-delete-category-${props.category.id}-btn`)
}

const deleteConfirmed = () => {
  alertScreenReader(`Deleting ${props.category.categoryType}`)
  deleteCategory(props.category.id).then(() => {
    alertScreenReader(`Deleted "${props.category.name}" ${props.category.categoryType}.`)
    isDeleting.value = false
    degreeStore.setDisableButtons(false)
    putFocusNextTick(`column-${props.position}-create-btn`)
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
  border-left: 3px solid rgb(var(--v-theme-primary));
  padding: 0 0 0 0.5em;
  margin: 0.2em 0 0.2em 0;
}
.drop-zone-container-subcategory {
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
