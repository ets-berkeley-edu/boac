<template>
  <div>
    <div class="d-flex flex-row justify-content-between w-50">
      <h2 class="page-section-header-sub">Unit Requirements</h2>
      <b-btn
        :id="`unit-requirement-col-${columnNumber}-create-link`"
        class="d-flex flex-row-reverse justify-content-end text-nowrap py-0"
        variant="link"
      >
        Add unit requirement
        <font-awesome icon="plus" class="m-1" />
      </b-btn>
    </div>
    <div v-if="$_.isEmpty(unitRequirements)" class="no-data-text">
      No unit requirements created
    </div>
    <b-table
      id="unit-requirements-table"
      :items="unitRequirements"
      :fields="fields"
      class="w-50"
      thead-class="sortable-table-header text-nowrap border-bottom"
      borderless
      responsive
    >
      <template #cell(actions)="row">
        <b-btn
          :id="`unit-requirement-${row.item.id}-edit-btn`"
          class="py-0"
          variant="link"
        >
          <font-awesome icon="edit" />
          <span class="sr-only">Edit {{ row.item.name }}</span>
        </b-btn>
        <b-btn
          :id="`unit-requirement-${row.item.id}-delete-btn`"
          class="py-0"
          variant="link"
        >
          <font-awesome icon="trash-alt" />
          <span class="sr-only">Delete {{ row.item.name }}</span>
        </b-btn>
      </template>
    </b-table>
    <hr />
    <b-container class="px-0 mx-0">
      <b-row>
        <b-col
          v-for="columnNumber in [1, 2, 3]"
          :key="columnNumber"
          class="degree-progress-column"
        >
          <div class="d-flex flex-row pb-3">
            <div class="pill degree-progress-pill px-2">{{ `Column ${columnNumber}` }}</div>
            <b-btn
              :id="`unit-requirement-col-${columnNumber}-create-link`"
              class="d-flex flex-row-reverse justify-content-end text-nowrap py-0"
              variant="link"
            >
              {{ `Add column ${columnNumber} requirement` }}
              <font-awesome icon="plus" class="m-1" />
            </b-btn>
          </div>
          <div v-if="$_.isEmpty(requirementCategoriesByColumn[columnNumber])" class="no-data-text pb-3">
            {{ `No column ${columnNumber} requirements` }}
          </div>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DegreeProgressEditSession from '@/mixins/DegreeProgressEditSession'
import Util from '@/mixins/Util'

export default {
  name: 'UnitRequirements',
  mixins: [Context, DegreeProgressEditSession, Util],
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
    ]
  }),
  computed: {
    requirementCategoriesByColumn() {
      return this.$_.groupBy(this.requirementCategories, 'columnNumber')
    }
  }
}
</script>

<style>
.degree-progress-column {
  min-width: 300px;
  padding-bottom: 10px;
}
.degree-progress-pill {
  background-color: #999;
  color: #fff;
  font-weight: 500;
  text-align: center;
  text-transform: uppercase;
  white-space: nowrap;
}
</style>