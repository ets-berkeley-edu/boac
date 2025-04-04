<template>
  <v-data-table-virtual
    :cell-props="data => ({
      class: 'px-1 vertical-top',
      'data-label': data.column.title,
      id: `td-term-${data.item.termId}-section-${data.item.sectionId}-column-${data.column.key}`,
      style: $vuetify.display.mdAndUp ? 'max-width: 200px;' : ''
    })"
    class="responsive-data-table"
    density="compact"
    :headers="headers"
    :items="items"
    mobile-breakpoint="md"
    must-sort
    no-sort-reset
    :row-props="data => ({
      id: `tr-term-${data.item.termId}-section-${data.item.sectionId}`
    })"
    :sort-by="[sortBy]"
    @update:sort-by="onUpdateSortBy"
  >
    <template #headers="{columns, isSorted, toggleSort, getSortIcon}">
      <tr>
        <th
          v-for="column in columns"
          :key="column.key"
          :aria-label="column.ariaLabel || column.title"
          :aria-sort="isSorted(column) ? `${sortBy.order}ending` : null"
          class="pl-0 pr-3"
        >
          <template v-if="column.sortable">
            <v-btn
              :id="`students-sort-by-${column.key}-btn`"
              :append-icon="getSortIcon(column)"
              :aria-label="`Sort by ${column.ariaLabel || column.title} ${isSorted(column) && sortBy.order === 'asc' ? 'descending' : 'ascending'}`"
              class="align-start font-size-12 font-weight-bold height-unset min-width-unset pa-1 text-uppercase v-table-sort-btn-override"
              :class="{'icon-visible': isSorted(column)}"
              color="body"
              density="compact"
              variant="plain"
              @click="() => toggleSort(column)"
            >
              <span class="text-left text-wrap">{{ column.title }}</span>
            </v-btn>
          </template>
          <template v-else>
            <div class="font-weight-bold line-height-normal pa-1">{{ column.title }}</div>
          </template>
        </th>
      </tr>
    </template>
    <template #item.section="{item}">
      <span class="sr-only">Section</span>
      <router-link class="font-weight-600" :to="`/course/${item.termId}/${item.sectionId}`">
        {{ item.courseName }} - {{ item.instructionFormat }} {{ item.sectionNum }}
      </router-link>
    </template>
    <template #item.courseName="{item}">
      <span class="sr-only">Course Name</span>
      {{ item.courseTitle }}
    </template>
    <template #item.instructors="{item}">
      <span v-if="size(item.instructors)">
        {{ item.instructors }}
      </span>
      <span v-if="!size(item.instructors)">
        &mdash;
      </span>
    </template>
  </v-data-table-virtual>
</template>

<script setup>
import {find, size} from 'lodash'
import {onMounted, ref} from 'vue'
import {alertScreenReader} from '@/lib/utils'

const props = defineProps({
  courses: {
    required: true,
    type: Array
  }
})

const headers = ref([])
const items = ref([])
const sortBy = ref({})

onMounted(() => {
  headers.value = [
    {key: 'section', sortable: true, sortRaw, title: 'Section', value: item => `${item.courseName} ${item.instructionFormat} ${item.sectionNum}`, width: '220px'},
    {key: 'courseName', sortable: true, sortRaw, title: 'Course Name', width: '360px'},
    {key: 'instructors', sortable: false, title: 'Instructor(s)'}
  ]
  sortBy.value = {key: 'section', order: 'asc'}
  items.value = [...props.courses].sort(sortRaw)
})

const onUpdateSortBy = primarySortBy => {
  const key = primarySortBy[0].key
  const header = find(headers.value, {key: key})
  sortBy.value = primarySortBy[0]
  if (header) {
    alertScreenReader(`Sorted by ${header.ariaLabel || header.title}, ${sortBy.value.order}ending`)
  }
}

const sortRaw = (c1, c2) => {
  if (sortBy.value.key === 'section') {
    // Compare by subject area.
    const split1 = splitCourseName(c1)
    const split2 = splitCourseName(c2)
    if (split1[0] > split2[0]) {
      return 1
    }
    if (split1[0] < split2[0]) {
      return -1
    }
    // If subject areas are identical, extract and compare numeric portion of catalog id.
    const code1 = parseInt(split1[1].match(/\d+/)[0], 10)
    const code2 = parseInt(split2[1].match(/\d+/)[0], 10)
    if (code1 > code2) {
      return 1
    }
    if (code1 < code2) {
      return -1
    }
    // If catalog ids are numerically identical then handle prefixes and suffixes with alphabetic comparison.
    if (split1[1] > split2[1]) {
      return 1
    }
    if (split1[1] < split2[1]) {
      return -1
    }
    // Instruction format and section number.
    if (c1.instructionFormat > c2.instructionFormat) {
      return 1
    }
    if (c1.instructionFormat < c2.instructionFormat) {
      return -1
    }
    return c1.sectionNum > c2.sectionNum ? 1 : -1
  } else if (sortBy.value.key === 'courseName') {
    return c1.courseName.localeCompare(c2.courseName, undefined, {usage: 'sort', numeric: true})
    // eslint-disable-next-line no-else-return
  } else {
    return 0
  }
}

const splitCourseName = course => {
  const split = course.courseName.split(' ')
  return [split.slice(0, -1).join(' '), split[split.length - 1]]
}
</script>
