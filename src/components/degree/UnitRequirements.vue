<template>
  <b-container class="px-0" fluid>
    <b-row>
      <b-col>
        <div class="align-items-start d-flex flex-row justify-content-between">
          <h2 class="font-size-20 font-weight-bold text-nowrap pb-2">Unit Requirements</h2>
          <b-btn
            v-if="$currentUser.canEditDegreeProgress"
            id="unit-requirement-create-link"
            class="pr-0 py-0"
            :disabled="!!editMode || disableButtons"
            variant="link"
            @click.prevent="onClickAdd"
          >
            <div class="align-items-center d-flex justify-content-between">
              <div class="pr-2 text-nowrap">
                Add unit requirement
              </div>
              <div>
                <font-awesome class="font-size-16" icon="plus" />
              </div>
            </div>
          </b-btn>
        </div>
        <div v-if="!editMode">
          <div v-if="$_.isEmpty(unitRequirements)" id="unit-requirements-no-data" class="no-data-text">
            No unit requirements created
          </div>
          <b-table-lite
            v-if="!$_.isEmpty(unitRequirements)"
            id="unit-requirements-table"
            :items="unitRequirements"
            :fields="fields"
            thead-class="sortable-table-header text-nowrap border-bottom"
            borderless
            small
          >
            <template v-if="$currentUser.canEditDegreeProgress" #cell(actions)="row">
              <b-btn
                :id="`unit-requirement-${row.item.id}-edit-btn`"
                class="pr-2 pt-0"
                :disabled="disableButtons"
                variant="link"
                @click.prevent="onClickEdit(row.index)"
              >
                <font-awesome icon="edit" />
                <span class="sr-only">Edit {{ row.item.name }}</span>
              </b-btn>
              <b-btn
                :id="`unit-requirement-${row.item.id}-delete-btn`"
                class="px-0 pt-0"
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
        <div v-if="editMode" class="mb-3">
          <EditUnitRequirement
            :index="indexOfSelected"
            :unit-requirement="unitRequirements[indexOfSelected]"
          />
        </div>
      </b-col>
    </b-row>
    <AreYouSureModal
      v-if="isDeleting"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      :modal-body="`Are you sure you want to delete <strong>${$_.get(selected, 'name')}</strong>?`"
      :show-modal="isDeleting"
      button-label-confirm="Delete"
      modal-header="Delete Unit Requirement"
    />
  </b-container>
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
        tdClass: 'font-size-16 pl-0 pt-2',
        thClass: 'faint-text font-size-12 pl-0 text-uppercase'
      },
      {
        key: 'minUnits',
        label: 'Min Units',
        tdClass: 'font-size-16 pl-0 pt-2 text-right',
        thClass: 'faint-text font-size-12 pl-0 text-uppercase'
      },
      {
        key: 'actions',
        label: '',
        tdClass: 'd-flex justify-content-end',
        thClass: 'faint-text font-size-12 pl-0 text-uppercase'
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
