<template>
  <div>
    <div
      id="drop-zone-category"
      class="w-100"
      :class="{
        'drop-zone-container': !size(category.subcategories) && !printable,
        'drop-zone-container-on': isDroppable() && degreeStore.draggingContext.target === category.id
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
          class="category-header"
          :class="{'font-size-14': printable, 'font-size-18': !printable}"
        >
          {{ category.name }}
        </h3>
        <h4
          v-if="category.categoryType === 'Subcategory'"
          class="subcategory-header"
          :class="{'font-size-12': printable, 'font-size-16': !printable}"
        >
          {{ category.name }}
        </h4>
        <div v-if="!degreeStore.sid && canEdit" class="align-items-start d-flex justify-content-end text-no-wrap">
          <v-btn
            :id="`column-${position}-edit-category-${category.id}-btn`"
            class="pr-1 pt-0"
            :disabled="disableButtons"
            size="small"
            variant="text"
            @click.prevent="edit"
          >
            <v-icon :icon="mdiNoteEditOutline" />
            <span class="sr-only">Edit {{ category.name }}</span>
          </v-btn>
          <v-btn
            :id="`column-${position}-delete-category-${category.id}-btn`"
            class="px-0 pt-0"
            :disabled="disableButtons"
            size="sm"
            variant="text"
            @click="deleteDegreeCategory"
          >
            <v-icon :icon="mdiTrashCanOutline" />
            <span class="sr-only">Delete {{ category.name }}</span>
          </v-btn>
        </div>
      </div>
      <div
        v-if="category.description"
        id="category-header-description"
        class="py-1"
        :class="{'font-size-12': printable, 'pl-1': !printable}"
      >
        <pre v-if="printable" class="text-wrap" v-html="category.description" />
        <span
          v-if="!printable"
          v-linkified
          class="text-wrap"
          v-html="category.description"
        />
      </div>
    </div>
    <AreYouSureModal
      v-model="isDeleting"
      button-label-confirm="Delete"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      :modal-header="`Delete ${category.categoryType}`"
    >
      Are you sure you want to delete <strong>&quot;{{ category.name }}&quot;</strong>
    </AreYouSureModal>
  </div>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {categoryHasCourse, isCampusRequirement} from '@/lib/degree-progress'
import {deleteCategory, onDrop} from '@/stores/degree-edit-session/utils'
import {mdiNoteEditOutline, mdiTrashCanOutline} from '@mdi/js'
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
  return deleteCategory(props.category.id).then(() => {
    alertScreenReader(`${props.category.name} deleted.`)
    isDeleting.value = false
    degreeStore.setDisableButtons(false)
    putFocusNextTick(`column-${props.position}-create-btn`)
  })
}

const deleteDegreeCategory = () => {
  degreeStore.setDisableButtons(true)
  isDeleting.value = true
  alertScreenReader(`Delete ${props.category.name}`)
}

const edit = () => {
  alertScreenReader(`Edit ${props.category.name}`)
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
pre {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  margin: 0;
}
.category-header {
  font-weight: bold;
  margin-bottom: 0;
  padding: 0;
}
.drop-zone-container {
  border-left: 2px solid #337ab7;
  padding: 0 0.3em 0 0.5em;
  margin: 0.2em 0 0.2em 0;
}
.drop-zone-container-on {
  background-color: #ecf5fb;
  border-left: 2px solid transparent;
  outline: #8bbdda dashed 0.15em;
}
.subcategory-header {
  font-weight: bold;
  margin-bottom: 0;
  padding: 0;
}
</style>
