<template>
  <b-container v-if="render" class="pl-0" fluid>
    <b-row>
      <b-col>
        <div class="align-items-start d-flex flex-row justify-content-between">
          <h3
            class="font-weight-bold pb-0 pr-2 text-nowrap"
            :class="{'font-size-12': printable, 'font-size-20': !printable}"
          >
            Unit Requirements
          </h3>
          <div v-if="$currentUser.canEditDegreeProgress && !sid && !printable">
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
          <div
            v-if="!items.length"
            id="unit-requirements-no-data"
            class="no-data-text pl-1"
            :class="{'font-size-12': printable}"
          >
            No unit requirements created
          </div>
          <b-table-lite
            v-if="items.length"
            id="unit-requirements-table"
            borderless
            :fields="fields"
            :foot-clone="!$_.isNil(sid)"
            :items="items"
            small
            thead-class="sortable-table-header text-nowrap border-bottom"
          >
            <template v-if="$currentUser.canEditDegreeProgress && !sid && !printable" #cell(actions)="row">
              <div class="align-items-center d-flex">
                <b-btn
                  :id="`unit-requirement-${row.item.id}-edit-btn`"
                  class="pr-2 pt-0"
                  :disabled="disableButtons"
                  size="sm"
                  variant="link"
                  @click.prevent="onClickEdit(row.item)"
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
                  @click.prevent="onClickDelete(row.item)"
                >
                  <font-awesome icon="trash-alt" />
                  <span class="sr-only">Delete {{ row.item.name }}</span>
                </b-btn>
              </div>
            </template>
            <template v-if="sid" #foot()="data">
              <div class="footer-cell" :class="{'font-size-12': printable, 'font-size-16': !printable}">
                <div v-if="data.field.key.toLowerCase() === 'name'" class="font-weight-bold">
                  Total Units
                </div>
                <div v-if="data.field.key.toLowerCase() === 'completed'" id="count-required-units-completed" class="pr-1">
                  {{ totalCompleted }}
                </div>
              </div>
            </template>
          </b-table-lite>
        </div>
        <div v-if="isEditing" class="mb-3">
          <EditUnitRequirement :on-exit="reset" :unit-requirement="selected" />
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
  props: {
    printable: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    fields: undefined,
    isDeleting: false,
    isEditing: false,
    items: undefined,
    render: false,
    selected: undefined,
    totalCompleted: undefined
  }),
  watch: {
    lastPageRefreshAt() {
      this.refresh()
    }
  },
  created() {
    const tdFontSize = this.printable ? 'font-size-12' : 'font-size-16'
    this.fields = [
      {
        key: 'name',
        label: 'Fulfillment Requirements',
        tdClass: `${tdFontSize} pl-0 pr-1 pt-1`,
        thClass: 'font-size-12 faint-text pl-0 pr-1 text-uppercase'
      },
      {
        key: 'minUnits',
        label: this.sid ? 'Min' : 'Min Units',
        tdClass: `${tdFontSize} pl-0 pr-1 pt-1 text-right`,
        thClass: 'font-size-12 faint-text pl-0 pr-1 text-right text-uppercase'
      }
    ]
    if (this.sid) {
      this.fields.push({
        key: 'completed',
        label: 'Completed',
        tdClass: `${tdFontSize} d-flex justify-content-end`,
        thClass: 'font-size-12 faint-text px-0 text-right text-uppercase'
      })
    } else if (this.$currentUser.canEditDegreeProgress) {
      this.fields.push({
        key: 'actions',
        label: '',
        tdClass: 'd-flex justify-content-end',
        thClass: 'font-size-12 faint-text px-0 text-uppercase'
      })
    }
    this.refresh()
    this.render = true
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
      this.deleteUnitRequirement(this.selected.id).then(() => {
        this.$announcer.polite(`${name} deleted.`)
        this.isDeleting = false
        this.setDisableButtons(false)
        this.$putFocusNextTick('unit-requirements-table')
      })
    },
    getUnitsCompleted(unitRequirement) {
      let count = 0
      this.$_.each(this.courses, courses => {
        this.$_.each(courses, course => {
          if (course.categoryId) {
            this.$_.each(course.unitRequirements, u => {
              if (u.id === unitRequirement.id) {
                count += course.units
              }
            })
          }
        })
      })
      return count
    },
    refresh() {
      const items = []
      this.totalCompleted = 0
      this.$_.each(this.unitRequirements, u => {
        const unitsCompleted = this.getUnitsCompleted(u)
        this.totalCompleted += unitsCompleted
        items.push({
          id: u.id,
          name: u.name,
          minUnits: u.minUnits,
          completed: unitsCompleted
        })
      })
      this.items = items
    },
    onClickAdd() {
      this.setDisableButtons(true)
      this.selected = null
      this.isEditing = true
    },
    onClickDelete(item) {
      this.setDisableButtons(true)
      this.selected = item
      this.isDeleting = true
    },
    onClickEdit(item) {
      this.setDisableButtons(true)
      this.selected = item
      this.isEditing = true
    },
    reset() {
      this.setDisableButtons(false)
      this.selected = null
      this.isEditing = false
      const focusId = this.selected ? `unit-requirement-${this.selected.id}-edit-btn` : 'unit-requirement-create-link'
      this.$putFocusNextTick(focusId)
    }
  }
}
</script>

<style scoped>
.footer-cell {
  border-top: 1px solid #999;
  color: #333;
  font-weight: bold;
  padding: 4px 0 4px 0;
  text-transform: none !important;
  width: 100%;
}
</style>
