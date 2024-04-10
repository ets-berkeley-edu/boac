<template>
  <div>
    <div
      id="drop-zone-category"
      class="w-100"
      :class="{
        'drop-zone-container': !_size(category.subcategories) && !printable,
        'drop-zone-container-on': isDroppable() && draggingContext.target === category.id
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
        <div v-if="!sid && canEdit" class="align-items-start d-flex justify-content-end text-no-wrap">
          <b-btn
            :id="`column-${position}-edit-category-${category.id}-btn`"
            class="pr-1 pt-0"
            :disabled="disableButtons"
            size="sm"
            variant="link"
            @click.prevent="edit"
          >
            <v-icon :icon="mdiNoteEditOutline" />
            <span class="sr-only">Edit {{ category.name }}</span>
          </b-btn>
          <b-btn
            :id="`column-${position}-delete-category-${category.id}-btn`"
            class="px-0 pt-0"
            :disabled="disableButtons"
            size="sm"
            variant="link"
            @click="deleteDegreeCategory"
          >
            <v-icon :icon="mdiTrashCanOutline" />
            <span class="sr-only">Delete {{ category.name }}</span>
          </b-btn>
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
      v-if="isDeleting"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      :show-modal="isDeleting"
      button-label-confirm="Delete"
      :modal-header="`Delete ${category.categoryType}`"
    >
      Are you sure you want to delete <strong>&quot;{{ category.name }}&quot;</strong>
    </AreYouSureModal>
  </div>
</template>

<script setup>
import {mdiNoteEditOutline, mdiTrashCanOutline} from '@mdi/js'
</script>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'
import {categoryHasCourse, isCampusRequirement} from '@/lib/degree-progress'
import {deleteCategory, onDrop} from '@/stores/degree-edit-session/utils'

export default {
  name: 'Category',
  components: {AreYouSureModal},
  mixins: [Context, DegreeEditSession, Util],
  props: {
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
  },
  data: () => ({
    canEdit: undefined,
    isDeleting: false
  }),
  computed: {
    isCampusRequirements() {
      return !this._isEmpty(this.category.courseRequirements) && this._every(this.category.courseRequirements, isCampusRequirement)
    }
  },
  created() {
    this.canEdit = this.currentUser.canEditDegreeProgress && !this.printable
  },
  methods: {
    deleteCanceled() {
      this.isDeleting = false
      this.alertScreenReader('Canceled. Nothing deleted.')
      this.setDisableButtons(false)
      this.putFocusNextTick(`column-${this.position}-delete-category-${this.category.id}-btn`)
    },
    deleteConfirmed() {
      return deleteCategory(this.category.id).then(() => {
        this.alertScreenReader(`${this.category.name} deleted.`)
        this.isDeleting = false
        this.setDisableButtons(false)
        this.putFocusNextTick(`column-${this.position}-create-btn`)
      })
    },
    deleteDegreeCategory() {
      this.setDisableButtons(true)
      this.isDeleting = true
      this.alertScreenReader(`Delete ${this.category.name}`)
    },
    edit() {
      this.alertScreenReader(`Edit ${this.category.name}`)
      this.onClickEdit(this.category)
    },
    isDroppable() {
      return this.category.id === this.draggingContext.target
        && !this.isCampusRequirements
        && !this._size(this.category.subcategories)
        && !categoryHasCourse(this.category, this.draggingContext.course)
    },
    onDrag(event, stage) {
      switch (stage) {
      case 'end':
        this.setDraggingTarget(null)
        this.draggingContextReset()
        break
      case 'enter':
      case 'over':
        event.stopPropagation()
        event.preventDefault()
        this.setDraggingTarget(this.category.id)
        break
      case 'leave':
        if (this._get(event.target, 'id') === 'drop-zone-category') {
          this.setDraggingTarget(null)
        }
        break
      case 'exit':
      default:
        break
      }
    },
    onDropCourse(event) {
      event.stopPropagation()
      event.preventDefault()
      if (this.isDroppable()) {
        onDrop(this.category, 'requirement')
      }
      this.setDraggingTarget(null)
      return false
    }
  }
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
