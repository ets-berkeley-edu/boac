<template>
  <b-container v-if="render" class="pl-0" fluid>
    <b-row>
      <b-col>
        <div class="align-items-start d-flex flex-row justify-content-between">
          <h3
            class="font-weight-bold pb-0 pr-2 text-nowrap"
            :class="{'font-size-14': printable, 'font-size-20': !printable}"
          >
            Unit Requirements
          </h3>
          <div v-if="currentUser.canEditDegreeProgress && !sid && !printable">
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
            :items="_filter(items, item => item.type === 'unitRequirement' || item.isExpanded)"
            small
            :tbody-tr-attr="getTableRowAttributes"
            thead-class="sortable-table-header text-nowrap border-bottom"
          >
            <template v-if="sid && !printable" #cell(name)="row">
              <div v-if="row.item.type === 'course'" class="pl-3">
                {{ row.item.name }}
              </div>
              <b-button
                v-if="row.item.type === 'unitRequirement'"
                :id="`unit-requirement-${row.item.id}-toggle`"
                block
                class="border-0 p-0"
                :class="{'shadow-none': !row.item.isExpanded}"
                variant="link"
                @click.prevent="toggleExpanded(row.item)"
              >
                <div class="d-flex text-left">
                  <div class="caret caret-column pale-blue">
                    <font-awesome :icon="row.item.isExpanded ? 'caret-down' : 'caret-right'" />
                  </div>
                  <div>
                    <span class="sr-only">{{ `${row.item.isExpanded ? 'Hide' : 'Show'} fulfillments of ` }}</span>
                    {{ row.item.name }}
                  </div>
                </div>
              </b-button>
              <div
                v-if="row.item.isExpanded && row.item.type === 'unitRequirement' && !row.item.children.length"
                :id="`unit-requirement-${row.item.id}-no-courses`"
                class="faint-text pb-1 pl-4 pt-1"
              >
                No courses
              </div>
            </template>
            <template v-if="currentUser.canEditDegreeProgress && !sid && !printable" #cell(actions)="row">
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
      :modal-body="`Are you sure you want to delete <strong>${_get(selected, 'name')}</strong>?`"
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
import store from '@/store'
import Util from '@/mixins/Util'
import {deleteUnitRequirement} from '@/api/degree'
import {refreshDegreeTemplate} from '@/store/modules/degree-edit-session/utils'

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
    selected: undefined
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
        thClass: 'font-size-12 pl-0 pr-1 text-uppercase'
      },
      {
        key: 'minUnits',
        label: this.sid ? 'Min' : 'Min Units',
        tdClass: `${tdFontSize} pl-0 pr-1 pt-1 text-right`,
        thClass: 'font-size-12 pl-0 pr-1 text-right text-uppercase'
      }
    ]
    if (this.sid) {
      this.fields.push({
        key: 'completed',
        label: 'Completed',
        tdClass: `${tdFontSize} d-flex justify-content-end`,
        thClass: 'font-size-12 px-0 text-right text-uppercase'
      })
    } else if (this.currentUser.canEditDegreeProgress) {
      this.fields.push({
        key: 'actions',
        label: '',
        tdClass: 'd-flex justify-content-end',
        thClass: 'font-size-12 px-0 text-uppercase'
      })
    }
    this.refresh()
    this.render = true
  },
  methods: {
    deleteCanceled() {
      this.isDeleting = false
      this.putFocusNextTick(`unit-requirement-${this._get(this.selected, 'id')}-delete-btn`)
      this.alertScreenReader('Canceled. Nothing deleted.')
      this.setDisableButtons(false)
    },
    deleteConfirmed() {
      const name = this._get(this.selected, 'name')
      const templateId = store.getters['degree/templateId']
      deleteUnitRequirement(this.selected.id).then(() => {
        refreshDegreeTemplate(templateId).then(() => {
          this.alertScreenReader(`${name} deleted.`)
          this.isDeleting = false
          this.setDisableButtons(false)
          this.putFocusNextTick('unit-requirement-create-link')
        })
      })
    },
    getTableRowAttributes(item) {
      const prefix = 'unit-requirement'
      return {
        id: item.type === 'course' ? `${prefix}-${item.parent.id}-course-${item.id}` : `${prefix}-${item.id}`
      }
    },
    getUnitsCompleted(unitRequirement) {
      let count = 0
      this._each(this.courses, courses => {
        this._each(courses, course => {
          if (course.categoryId) {
            this._each(course.unitRequirements, u => {
              if (u.id === unitRequirement.id) {
                count += course.units
              }
            })
          }
        })
      })
      return count
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
    refresh() {
      const expandedIds = this._map((this._filter(this.items, 'isExpanded')), 'id')
      const items = []
      this._each(this.unitRequirements, u => {
        const isExpanded = expandedIds.includes(u.id)
        const unitRequirement = {
          id: u.id,
          children: [],
          completed: this.getUnitsCompleted(u),
          isExpanded,
          minUnits: u.minUnits,
          name: u.name,
          type: 'unitRequirement'
        }
        items.push(unitRequirement)
        if (this.sid) {
          let courses = this._filter(this.courses.assigned, course => {
            return !!this._find(course.unitRequirements, ['id', u.id])
          })
          courses = this._sortBy(courses, ['name', 'id'])
          this._each(courses, course => {
            const child = {
              id: course.id,
              completed: course.units,
              isExpanded,
              name: course.name,
              parent: {id: unitRequirement.id},
              type: 'course'
            }
            items.push(child)
            unitRequirement.children.push(child)
          })
        }
      })
      this.items = items
    },
    reset() {
      this.setDisableButtons(false)
      this.selected = null
      this.isEditing = false
      const focusId = this.selected ? `unit-requirement-${this.selected.id}-edit-btn` : 'unit-requirement-create-link'
      this.putFocusNextTick(focusId)
    },
    toggleExpanded(item) {
      const value = !item.isExpanded
      item.isExpanded = value
      this._each(item.children, child => child.isExpanded = value)
    }
  }
}
</script>

<style scoped>
.caret-column {
  width: 1.3rem;
}
</style>
