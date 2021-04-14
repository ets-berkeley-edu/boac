<template>
  <div>
    <div class="d-flex flex-row justify-content-between w-50">
      <h2 class="page-section-header-sub pb-2">Unit Requirements</h2>
      <b-btn
        v-if="$currentUser.canEditDegreeProgress"
        id="unit-requirement-create-link"
        class="degree-progress-btn-link text-nowrap py-0"
        variant="link"
        :disabled="!!editMode || disableButtons"
        @click.prevent="onClickAdd"
      >
        Add unit requirement
        <font-awesome icon="plus" class="m-1" />
      </b-btn>
    </div>
    <div v-if="!editMode">
      <div v-if="$_.isEmpty(unitRequirements)" id="unit-requirements-no-data" class="no-data-text">
        No unit requirements created
      </div>
      <b-table-lite
        id="unit-requirements-table"
        :items="unitRequirements"
        :fields="fields"
        class="w-50"
        thead-class="sortable-table-header text-nowrap border-bottom"
        borderless
        responsive
        small
      >
        <template v-if="$currentUser.canEditDegreeProgress" #cell(actions)="row">
          <b-btn
            :id="`unit-requirement-${row.item.id}-edit-btn`"
            class="py-0"
            :disabled="disableButtons"
            variant="link"
            @click.prevent="onClickEdit(row.index)"
          >
            <font-awesome icon="edit" />
            <span class="sr-only">Edit {{ row.item.name }}</span>
          </b-btn>
          <b-btn
            :id="`unit-requirement-${row.item.id}-delete-btn`"
            class="py-0"
            :disabled="disableButtons"
            variant="link"
            @click.prevent="onClickDelete(row.index)"
          >
            <font-awesome icon="trash-alt" />
            <span class="sr-only">Delete {{ row.item.name }}</span>
          </b-btn>
        </template>
      </b-table-lite>
    </div>
    <EditUnitRequirement
      v-if="editMode"
      :index="indexOfSelected"
      :unit-requirement="unitRequirements[indexOfSelected]"
    />
    <AreYouSureModal
      v-if="isDeleting"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      :modal-body="`Are you sure you want to delete <strong>${$_.get(selected, 'name')}</strong>?`"
      :show-modal="isDeleting"
      button-label-confirm="Delete"
      modal-header="Delete Unit Requirement"
    />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import EditUnitRequirement from '@/components/degree/EditUnitRequirement'
import Util from '@/mixins/Util'

export default {
  name: 'UnitRequirements',
  components: {AreYouSureModal, EditUnitRequirement},
  mixins: [Context, DegreeEditSession, Util],
  data: () => ({
    fields: [
      {
        key: 'name',
        label: 'Fulfillment Requirements',
        class: 'pl-0'
      },
      {
        key: 'minUnits',
        label: 'Min Units',
        class: 'text-right'
      },
      {
        key: 'actions',
        label: '',
        class: 'd-flex flex-row justify-content-end pr-0'
      }
    ],
    indexOfSelected: undefined,
    isDeleting: false
  }),
  computed: {
    selected() {
      return this.unitRequirements[this.indexOfSelected]
    }
  },
  methods: {
    deleteCanceled() {
      this.isDeleting = false
      this.putFocusNextTick(`unit-requirement-${this.$_.get(this.selected, 'id')}-delete-btn`)
      this.$announcer.polite('Canceled. Nothing deleted.')
      this.setDisableButtons(false)
    },
    deleteConfirmed() {
      const name = this.$_.get(this.selected, 'name')
      this.deleteUnitRequirement(this.indexOfSelected).then(() => {
        this.$announcer.polite(`${name} deleted.`)
        this.isDeleting = false
        this.setDisableButtons(false)
        this.putFocusNextTick('unit-requirements-table')
      })
    },
    onClickAdd() {
      this.setDisableButtons(true)
      this.indexOfSelected = null
      this.setEditMode('createUnitRequirement')
    },
    onClickDelete(index) {
      this.setDisableButtons(true)
      this.indexOfSelected = index
      this.isDeleting = true
    },
    onClickEdit(index) {
      this.setDisableButtons(true)
      this.indexOfSelected = index
      this.setEditMode('updateUnitRequirement')
    },
  }
}
</script>
