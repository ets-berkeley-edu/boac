<template>
  <div>
    <div
      id="drop-zone-category"
      class="align-items-center d-flex drop-zone justify-content-between w-100"
      :class="{
        'drop-zone-on': isDroppable(category) && draggingContext.target === category.id,
        'drop-zone-off': !isDroppable(category) || draggingContext.target !== category.id
      }"
      @dragend="onDrag($event, 'end')"
      @dragenter="onDrag($event, 'enter')"
      @dragleave="onDrag($event, 'leave')"
      @dragover="onDrag($event, 'over')"
      @dragstart="onDrag($event, 'start')"
      @drop="onDropCourse($event)"
    >
      <div>
        <h2 v-if="category.categoryType === 'Category'" class="degree-progress-category pl-0">
          {{ category.name }}
        </h2>
        <h3 v-if="category.categoryType === 'Subcategory'" class="degree-progress-subcategory pl-0">
          {{ category.name }}
        </h3>
      </div>
      <div
        v-if="!sid && $currentUser.canEditDegreeProgress"
        class="align-items-start d-flex justify-content-end text-nowrap"
      >
        <b-btn
          :id="`column-${position}-edit-category-${category.id}-btn`"
          class="pr-1 pt-0"
          :disabled="disableButtons"
          size="sm"
          variant="link"
          @click.prevent="edit"
        >
          <font-awesome icon="edit" />
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
          <font-awesome icon="trash-alt" />
          <span class="sr-only">Delete {{ category.name }}</span>
        </b-btn>
      </div>
    </div>
    <div v-if="category.description" id="degree-progress-category-description">
      {{ category.description }}
    </div>
    <AreYouSureModal
      v-if="isDeleting"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      :modal-body="`Are you sure you want to delete <strong>&quot;${category.name}&quot;</strong>`"
      :show-modal="isDeleting"
      button-label-confirm="Delete"
      :modal-header="`Delete ${category.categoryType}`"
    />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'

export default {
  name: 'Category',
  mixins: [DegreeEditSession, Util],
  components: {AreYouSureModal},
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
      required: false,
      type: Function
    }
  },
  data: () => ({
    isDeleting: false
  }),
  computed: {
    parents() {
      return this.$_.filter(this.categories, c => {
        return c.position === this.position && this.$_.isNil(c.parentCategoryId)
      })
    }
  },
  methods: {
    deleteCanceled() {
      this.isDeleting = false
      this.$putFocusNextTick(`column-${this.position}-delete-category-${this.category.id}-btn`)
      this.$announcer.polite('Canceled. Nothing deleted.')
      this.setDisableButtons(false)
    },
    deleteConfirmed() {
      this.deleteCategory(this.category.id).then(() => {
        this.$announcer.polite(`${this.category.name} deleted.`)
        this.isDeleting = false
        this.setDisableButtons(false)
        this.$putFocusNextTick('page-header')
      })
    },
    deleteDegreeCategory() {
      this.setDisableButtons(true)
      this.isDeleting = true
      this.$announcer.polite(`Delete ${this.category.name}`)
    },
    edit() {
      this.$announcer.polite(`Edit ${this.category.name}`)
      this.onClickEdit(this.category)
    },
    isDroppable() {
      return this.category.id === this.draggingContext.target && !this.$_.size(this.category.subcategories)
    },
    onDrag(event, stage) {
      switch (stage) {
      case 'end':
        this.setDraggingTarget(null)
        this.onDragEnd()
        break
      case 'enter':
      case 'over':
        event.stopPropagation()
        event.preventDefault()
        this.setDraggingTarget(this.category.id)
        break
      case 'leave':
        if (this.$_.get(event.target, 'id') === 'drop-zone-category') {
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
      this.onDrop({category: this.category, context: 'requirement'})
      this.setDraggingTarget(null)
      return false
    }
  }
}
</script>

<style scoped>
.drop-zone {
  padding: 0.15em
}
.drop-zone-on {
  background-color: #ecf5fb;
  cursor: move;
  outline: #8bbdda dashed 0.05em;
}
</style>
