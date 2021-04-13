<template>
  <div class="align-items-center d-flex justify-content-between pl-2">
    <div
      :class="{
        'font-weight-500 pt-1': category.categoryType === 'Category',
        'font-size-14 pt-0': category.categoryType === 'Subcategory'
      }"
    >
      {{ category.name }}
    </div>
    <div v-if="category.description">
      {{ category.description }}
    </div>
    <div class="float-right">
      <b-btn
        :id="`column-${position}-edit-category-${category.id}-btn`"
        class="py-0 pr-0"
        :disabled="disableButtons"
        variant="link"
        @click.prevent="editCategory"
      >
        <font-awesome icon="edit" />
        <span class="sr-only">Edit {{ category.name }}</span>
      </b-btn>
      <b-btn
        :id="`column-${position}-delete-category-${category.id}-btn`"
        class="py-0"
        :disabled="disableButtons"
        variant="link"
        @click="deleteDegreeCategory"
      >
        <font-awesome icon="trash-alt" />
        <span class="sr-only">Delete {{ category.name }}</span>
      </b-btn>
    </div>
    <AreYouSureModal
      v-if="isDeleting"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      :modal-body="`Are you sure you want to delete <strong>&quot;${category.name}&quot;</strong>`"
      :show-modal="isDeleting"
      button-label-confirm="Delete"
      modal-header="Delete Degree"
    />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'

export default {
  name: 'DegreeTemplateCategory',
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
      this.putFocusNextTick(`column-${this.position}-delete-category-${this.category.id}-btn`)
      this.$announcer.polite('Canceled. Nothing deleted.')
      this.setDisableButtons(false)
    },
    deleteConfirmed() {
      this.deleteCategory(this.category.id).then(() => {
        this.$announcer.polite(`${this.category.name} deleted.`)
        this.isDeleting = false
        this.setDisableButtons(false)
        this.putFocusNextTick('page-header')
      })
    },
    deleteDegreeCategory() {
      this.setDisableButtons(true)
      this.isDeleting = true
      this.$announcer.polite(`Delete ${this.category.name}`)
    },
    editCategory() {
      this.$announcer.polite(`Edit ${this.category.name}`)
    }
  }
}
</script>
