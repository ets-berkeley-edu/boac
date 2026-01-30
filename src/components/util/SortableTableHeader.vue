<template>
  <tr>
    <template v-if="!isCompact">
      <th
        v-for="column in columns"
        :key="column.key"
        :aria-label="column.ariaLabel || column.title"
        :aria-sort="isSorted(column) ? (sortDesc ? 'descending' : 'ascending') : 'none'"
        class="px-0"
        :class="column.class"
        scope="col"
        :style="column.headerProps"
      >
        <v-btn
          v-if="column.sortable && !disableSort"
          :id="`${idPrefix}-sort-col-${column.value}-btn`"
          :append-icon="sortIcon(column)"
          :aria-label="`Sort by ${column.ariaLabel || column.title} ${isSorted(column) && !sortDesc ? 'descending' : 'ascending'}, ${tableName}`"
          block
          class="sort-col-btn font-weight-bold text-no-wrap text-uppercase v-table-sort-btn-override"
          :class="{
            'icon-visible': isSorted(column),
            'ml-auto': column.align === 'end',
            'mx-auto': column.align === 'center'
          }"
          color="body"
          density="compact"
          size="small"
          variant="plain"
          @click="() => onToggleSort(column)"
        >
          {{ column.title }}
        </v-btn>
        <div
          v-if="!column.sortable || disableSort"
          class="sort-col-btn font-weight-bold d-flex align-center"
          :class="{'justify-end': column.align === 'end'}"
        >
          <span :class="get(column, 'headerProps.class', '')">{{ column.title }}</span>
        </div>
      </th>
    </template>
    <th v-if="isCompact" :colspan="columns.length">
      <div v-if="size(sortColumnOptions)" class="d-flex align-baseline pb-4 w-100 w-sm-75 w-lg-50">
        <label class="text-no-wrap" :for="`${idPrefix}-sort-col-select`">
          Sort by
        </label>
        <select
          :id="`${idPrefix}-sort-col-select`"
          :aria-label="`Sort ${tableName} by`"
          autocomplete="off"
          class="select-menu w-100 mb-2 ml-2"
          :model-value="selectedSortColumn"
          @change="onSelectSortColumn"
        >
          <option
            v-for="col in sortColumnOptions"
            :key="col.title"
            :aria-label="col.ariaLabel || col.title"
            :selected="col.title === selectedSortColumn.title"
            :value="col.title"
          >
            {{ col.title }}
          </option>
        </select>
      </div>
    </th>
  </tr>
</template>

<script setup>
import {filter, find, flatMap, get, size} from 'lodash'
import {computed, defineModel, nextTick, onMounted, ref} from 'vue'

const props = defineProps({
  columns: {
    required: true,
    type: Array
  },
  disableSort: {
    required: false,
    type: Boolean
  },
  idPrefix: {
    default: 'table',
    required: false,
    type: String
  },
  isCompact: {
    required: false,
    type: Boolean
  },
  isSorted: {
    required: true,
    type: Function
  },
  toggleSort: {
    required: true,
    type: Function
  },
  setOrder: {
    required: true,
    type: Function
  },
  sortedBy: {
    required: true,
    type: Object
  },
  sortIcon: {
    default: () => {},
    required: false,
    type: Function
  },
  tableName: {
    default: '',
    required: false,
    type: String
  }
})

const selectedSortColumn = defineModel({type: Object})
const sortColumnOptions = ref([])

const sortDesc = computed(() => get(props.sortedBy, 'order') === 'desc')

onMounted(() => {
  sortColumnOptions.value = flatMap(filter(props.columns, 'sortable'), col => {
    return [
      {
        ...col,
        ariaLabel: col.ariaLabel ? `${col.ariaLabel}, ascending` : undefined,
        order: 'asc',
        title: `${col.title}, ascending`,
      },
      {
        ...col,
        ariaLabel: col.ariaLabel ? `${col.ariaLabel}, descending` : undefined,
        order: 'desc',
        title: `${col.title}, descending`
      }
    ]
  })
  selectedSortColumn.value = find(sortColumnOptions.value, props.sortedBy)
})

const onSelectSortColumn = e => {
  const column = find(sortColumnOptions.value, {'title': e.target.value})
  selectedSortColumn.value = column
  props.setOrder([{key: column.key, order: column.order}])
}

const onToggleSort = column => {
  props.toggleSort(column)
  nextTick(() => {
    selectedSortColumn.value = find(sortColumnOptions.value, props.sortedBy)
  })
}
</script>

<style scoped>
.sort-col-btn {
  height: 28px !important;
  letter-spacing: normal !important;
  margin: 0 4px 0 -.1em;
  min-width: 0px !important;
  padding: 0 2px 0 4px;
}
</style>

<style>
.v-table-sort-btn-override .v-btn__append {
  margin-inline: 2px 1px !important;
}
.v-table-sort-btn-override .v-btn__append .v-icon {
  opacity: 0;
}
.v-table-sort-btn-override .v-btn__content {
  text-align: left;
}
.v-table-sort-btn-override:active .v-btn__append .v-icon,
.v-table-sort-btn-override:hover .v-btn__append .v-icon,
.v-table-sort-btn-override:focus .v-btn__append .v-icon {
  opacity: var(--v-medium-emphasis-opacity);
}
.v-table-sort-btn-override.icon-visible .v-btn__append .v-icon {
  opacity: 1;
}
</style>
