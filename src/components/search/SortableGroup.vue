<template>
  <v-expansion-panel
    :id="`sortable-${keyword}-${props.group.id}`"
    :bg-color="isOpen ? 'pale-blue' : 'transparent'"
    class="sortable-group"
    :class="isOpen ? 'border-1' : 'border-0'"
    hide-actions
    rounded
    @group:selected="fetchStudents"
  >
    <v-expansion-panel-title
      :id="`sortable-${keyword}-${props.group.id}-expand-btn`"
      class="bg-transparent pl-2 py-1 w-100"
      hide-actions
    >
      <template #default="{expanded}">
        <div class="d-flex justify-space-between w-100">
          <div class="align-center d-flex">
            <div class="expand-icon-container">
              <v-progress-circular
                v-if="isFetching && group.alertCount > 0"
                color="primary"
                indeterminate
                size="x-small"
                width="2"
              />
              <v-icon
                v-if="!isFetching"
                color="primary"
                :icon="expanded ? mdiMenuDown : mdiMenuRight"
                size="large"
              />
            </div>
            <h3 class="page-section-header-sub pr-8 text-primary">
              <span class="sr-only">{{ `${isOpen ? 'Hide' : 'Show'} details for ${groupTypeName} ` }}</span>
              {{ group.name }}<span class="sr-only">: </span>
              (<span :id="`sortable-${keyword}-${group.id}-total-student-count`">{{ group.totalStudentCount }}</span>
              <span class="sr-only">&nbsp;students.</span>)
            </h3>
          </div>
          <div class="d-flex align-center">
            <div v-if="!compact" class="pr-2 text-no-wrap">
              Total Alerts:
            </div>
            <PillCount
              v-if="!group.alertCount"
              :id="`sortable-${keyword}-${group.id}-total-alerts-count`"
              :aria-label="`No alerts for ${groupTypeName} '${group.name}'`"
              color="grey"
            >
              0
            </PillCount>
            <PillCount
              v-if="group.alertCount"
              :id="`sortable-${keyword}-${group.id}-total-alerts-count`"
              :aria-label="`${pluralize('alert', group.alertCount)} for ${groupTypeName} '${group.name}'`"
              class="px-2"
              color="warning"
            >
              {{ group.alertCount }}
            </PillCount>
          </div>
        </div>
      </template>
    </v-expansion-panel-title>
    <v-expansion-panel-text :id="`sortable-${keyword}-${props.group.id}-details`" class="bg-transparent">
      <div v-if="size(studentsWithAlerts)">
        <div
          v-if="!compact && size(studentsWithAlerts) === 50"
          :id="`sortable-${keyword}-${group.id}-alert-limited`"
          class="px-3"
        >
          Showing 50 students with a high number of alerts.
          <router-link
            :id="`sortable-${keyword}-${group.id}-alert-limited-view-all`"
            :to="getRoutePath(group)"
          >
            View all {{ group.totalStudentCount }} students in {{ groupTypeName }} "{{ group.name }}"
          </router-link>
        </div>
        <div class="ma-4">
          <SortableStudents
            class="bg-pale-blue"
            :compact="compact"
            domain="default"
            :sort-by="{key: 'alertCount', order: 'desc'}"
            :students="studentsWithAlerts"
          />
        </div>
      </div>
      <div
        v-if="openAndLoaded"
        :class="{'pa-3': group.totalStudentCount, 'pb-4 px-3': !group.totalStudentCount}"
      >
        <router-link
          :id="`sortable-${keyword}-${group.id}-view-all`"
          class="text-primary font-weight-regular"
          :to="getRoutePath(group)"
        >
          <span v-if="group.totalStudentCount">
            View {{ pluralize('student', group.totalStudentCount, {1: 'the one', 'other': `all ${group.totalStudentCount}`}) }}
            in {{ groupTypeName }} "{{ group.name }}"
          </span>
          <div v-if="!group.totalStudentCount" class="pl-3">
            {{ capitalize(groupTypeName) }} "{{ group.name }}" has zero students.
          </div>
        </router-link>
      </div>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script setup>
import PillCount from '@/components/util/PillCount'
import SortableStudents from '@/components/search/SortableStudents'
import {alertScreenReader, pluralize} from '@/lib/utils'
import {computed, ref} from 'vue'
import {getStudentsWithAlerts as getCohortStudentsWithAlerts} from '@/api/cohort'
import {getStudentsWithAlerts as getCuratedStudentsWithAlerts} from '@/api/curated'
import {mdiMenuDown, mdiMenuRight} from '@mdi/js'
import {capitalize, isNil, size} from 'lodash'

const props = defineProps({
  compact: {
    type: Boolean
  },
  group: {
    required: true,
    type: Object
  },
  isCohort: {
    required: true,
    type: Boolean
  }
})

const groupTypeName = props.isCohort ? 'cohort' : 'curated group'
const keyword = props.isCohort ? 'cohort' : 'curated'
const isFetching = ref(false)
const isOpen = ref(false)
const studentsWithAlerts = ref(undefined)

const openAndLoaded = computed({
  get: function() {
    return isOpen.value && !isFetching.value
  },
  set: function(value) {
    isOpen.value = value
  }
})

const fetchStudents = param => {
  isOpen.value = param.value
  if (isNil(studentsWithAlerts.value)) {
    isFetching.value = true
    const apiCall = props.isCohort ? getCohortStudentsWithAlerts : getCuratedStudentsWithAlerts
    apiCall(props.group.id).then(students => {
      studentsWithAlerts.value = students
      isFetching.value = false
      alertScreenReader(`Loaded students with alerts who are in ${groupTypeName} ${props.group.name}`)
    })
  }
}

const getRoutePath = group => {
  return `/${keyword}/${group.id}?domain=${group.domain}`
}
</script>

<style scoped>
.expand-icon-container {
  max-width: 40px;
  min-width: 40px;
  text-align: center;
}
.sortable-group {
  border: 1px solid rgb(var(--v-theme-primary));
}
</style>

<style lang="scss">
.sortable-group {
  &.v-expansion-panel::after {
    border: none !important;
  }
  .v-expansion-panel-text__wrapper {
    padding: 0;
  }
}
</style>
