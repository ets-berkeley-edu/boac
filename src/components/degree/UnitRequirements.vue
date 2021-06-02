<template>
  <b-container v-if="fields" class="pl-0" fluid>
    <b-row>
      <b-col>
        <div class="align-items-start d-flex flex-row justify-content-between">
          <h2 class="font-size-20 font-weight-bold pb-0 pr-2 text-nowrap">Unit Requirements</h2>
          <div v-if="$currentUser.canEditDegreeProgress && !sid">
            <b-btn
              id="unit-requirement-create-link"
              class="pr-0 py-0"
              :disabled="disableButtons"
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
        </div>
        <div v-if="!isEditing">
          <div v-if="!unitRequirements.length" id="unit-requirements-no-data" class="no-data-text pl-1">
            No unit requirements created
          </div>
          <b-table-lite
            v-if="unitRequirements.length"
            id="unit-requirements-table"
            :items="unitRequirements"
            :fields="fields"
            thead-class="sortable-table-header text-nowrap border-bottom"
            borderless
            small
          >
            <template v-if="$currentUser.canEditDegreeProgress && !sid" #cell(actions)="row">
              <div class="align-items-center d-flex">
                <b-btn
                  :id="`unit-requirement-${row.item.id}-edit-btn`"
                  class="pr-2 pt-0"
                  :disabled="disableButtons"
                  size="sm"
                  variant="link"
                  @click.prevent="onClickEdit(row.index)"
                >
                  <font-awesome icon="edit" />
                  <span class="sr-only">Edit {{ row.item.name }}</span>
                </b-btn>
              </div>
              <div>
                <b-btn
                  :id="`unit-requirement-${row.item.id}-delete-btn`"
                  class="px-0 pt-0"
                  :disabled="disableButtons"
                  size="sm"
                  variant="link"
                  @click.prevent="onClickDelete(row.index)"
                >
                  <font-awesome icon="trash-alt" />
                  <span class="sr-only">Delete {{ row.item.name }}</span>
                </b-btn>
              </div>
            </template>
          </b-table-lite>
        </div>
        <div v-if="isEditing" class="mb-3">
          <EditUnitRequirement
            :index="indexOfSelected"
            :on-exit="reset"
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
    fields: undefined,
    indexOfSelected: undefined,
    isDeleting: false,
    isEditing: false
  }),
  computed: {
    selected() {
      return this.indexOfSelected && this.unitRequirements[this.indexOfSelected]
    }
  },
  created() {
    this.fields = [
      {
        key: 'name',
        label: 'Fulfillment Requirements',
        tdClass: 'font-size-16 pl-0 pt-1',
        thClass: 'faint-text font-size-12 pl-0 text-uppercase'
      },
      {
        key: 'minUnits',
        label: this.sid ? 'Min' : 'Min Units',
        tdClass: 'font-size-16 pl-0 pt-1 text-right',
        thClass: 'faint-text font-size-12 pl-0 text-right text-uppercase'
      }
    ]
    if (this.sid) {
      this.fields.push({
        key: 'completed',
        label: 'Completed',
        tdClass: 'd-flex justify-content-end',
        thClass: 'faint-text font-size-12 pl-0 text-right text-uppercase'
      })
    } else if (this.$currentUser.canEditDegreeProgress) {
      this.fields.push({
        key: 'actions',
        label: '',
        tdClass: 'd-flex justify-content-end',
        thClass: 'faint-text font-size-12 pl-0 text-uppercase'
      })
    }
  },
  methods: {
    deleteCanceled() {
      this.isDeleting = false
      this.$putFocusNextTick(`unit-requirement-${this.$_.get(this.selected, 'id')}-delete-btn`)
      this.$announcer.polite('Canceled. Nothing deleted.')
      this.setDisableButtons(false)
    },
    deleteConfirmed() {
      const name = this.$_.get(this.selected, 'name')
      this.deleteUnitRequirement(this.indexOfSelected).then(() => {
        this.$announcer.polite(`${name} deleted.`)
        this.isDeleting = false
        this.setDisableButtons(false)
        this.$putFocusNextTick('unit-requirements-table')
      })
    },
    onClickAdd() {
      this.setDisableButtons(true)
      this.indexOfSelected = null
      this.isEditing = true
    },
    onClickDelete(index) {
      this.setDisableButtons(true)
      this.indexOfSelected = index
      this.isDeleting = true
    },
    onClickEdit(index) {
      this.setDisableButtons(true)
      this.indexOfSelected = index
      this.isEditing = true
    },
    reset() {
      const focusId = this.$_.isNil(this.indexOfSelected) ? 'unit-requirement-create-link' : `unit-requirement-${this.unitRequirements[this.indexOfSelected].id}-edit-btn`
      this.setDisableButtons(false)
      this.indexOfSelected = null
      this.isEditing = false
      this.$putFocusNextTick(focusId)
    }
  }
}
</script>
