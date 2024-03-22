<template>
  <v-expansion-panel
    :id="id"
    :bg-color="isOpen ? 'pale-blue' : 'transparent'"
    class="sortable-group"
    :class="isOpen ? 'border-1' : 'border-0'"
    elevation="0"
    rounded
    @group:selected="fetchStudents"
  >
    <v-expansion-panel-title
      :id="`${id}-expand-btn`"
      class="bg-transparent px-3 w-100"
      hide-actions
    >
      <template #default="{expanded}">
        <div class="d-flex justify-space-between align-baseline w-100">
          <div class="text-primary d-flex align-center">
            <div class="pr-2">
              <v-progress-circular
                v-if="isFetching"
                color="primary"
                indeterminate
                size="small"
              />
              <v-icon
                v-if="!isFetching"
                color="primary"
                :icon="expanded ? mdiMenuDown : mdiMenuRight"
                size="x-large"
              />
            </div>
            <h3 class="page-section-header-sub">
              <span class="sr-only">{{ `${isOpen ? 'Hide' : 'Show'} details for ${groupTypeName} ` }}</span>
              {{ group.name }}
              (<span :id="`sortable-${keyword}-${group.id}-total-student-count`">{{ group.totalStudentCount }}</span>
              <span class="sr-only">&nbsp;students</span>)
            </h3>
          </div>
          <div class="count d-flex align-center">
            <div v-if="!compact" class="pr-2 sortable-table-header">
              Total Alerts:
            </div>
            <PillAlert
              v-if="!group.alertCount"
              :aria-label="`No issues for ${groupTypeName} '${group.name}'`"
              color="grey"
            >
              0
            </PillAlert>
            <PillAlert
              v-if="group.alertCount"
              :aria-label="`${group.alertCount} alerts for ${groupTypeName} '${group.name}'`"
              class="px-2"
              color="warning"
            >
              {{ group.alertCount }}
            </PillAlert>
          </div>
        </div>
      </template>
    </v-expansion-panel-title>
    <v-expansion-panel-text :id="`${id}-details`" class="bg-transparent">
      <div v-if="_size(studentsWithAlerts)">
        <div
          v-if="!compact && _size(studentsWithAlerts) === 50"
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
        <div class="pt-4">
          <SortableStudents
            :id="`${id}-students`"
            domain="default"
            :students="studentsWithAlerts"
            :options="sortableGroupOptions"
          />
        </div>
      </div>
      <div v-if="openAndLoaded" class="pa-3">
        <router-link
          :id="`sortable-${keyword}-${group.id}-view-all`"
          class="text-primary font-weight-regular"
          :to="getRoutePath(group)"
        >
          <span v-if="group.totalStudentCount">
            View {{ pluralize('student', group.totalStudentCount, {1: 'the one', 'other': `all ${group.totalStudentCount}`}) }}
            in {{ groupTypeName }} "{{ group.name }}"
          </span>
          <div v-if="!group.totalStudentCount" class="pt-3">
            {{ _capitalize(groupTypeName) }} "{{ group.name }}" has 0 students
          </div>
        </router-link>
      </div>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script setup>
import {mdiMenuDown, mdiMenuRight} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import PillAlert from '@/components/util/PillAlert'
import SortableStudents from '@/components/search/SortableStudents'
import Util from '@/mixins/Util'
import {getStudentsWithAlerts as getCohortStudentsWithAlerts} from '@/api/cohort'
import {getStudentsWithAlerts as getCuratedStudentsWithAlerts} from '@/api/curated'

export default {
  name: 'SortableGroup',
  components: {PillAlert, SortableStudents},
  mixins: [Context, Util],
  props: {
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
  },
  data: () => ({
    buttonHasFocus: false,
    groupTypeName: undefined,
    isFetching: false,
    isOpen: false,
    keyword: undefined,
    studentsWithAlerts: undefined
  }),
  computed: {
    id() {
      return `sortable-${this.keyword}-${this.group.id}`
    },
    openAndLoaded: {
      get: function() {
        return this.isOpen && !this.isFetching
      },
      set: function(value) {
        this.isOpen = value
      }
    },
    sortableGroupOptions() {
      return {
        compact: this.compact,
        includeCuratedCheckbox: false,
        reverse: true,
        sortBy: ['alertCount']
      }
    }
  },
  mounted() {
    this.keyword = this.isCohort ? 'cohort' : 'curated'
    this.groupTypeName = this.isCohort ? 'cohort' : 'curated group'
  },
  methods: {
    fetchStudents(param) {
      this.isOpen = param.value
      if (this._isNil(this.studentsWithAlerts)) {
        this.isFetching = true
        const apiCall = this.isCohort ? getCohortStudentsWithAlerts : getCuratedStudentsWithAlerts
        apiCall(this.group.id).then(students => {
          this.studentsWithAlerts = students
          this.isFetching = false
          this.alertScreenReader(`Loaded students with alerts who are in ${this.groupTypeName} ${this.group.name}`)
        })
      }
    },
    getRoutePath(group) {
      return `/${this.keyword}/${group.id}?domain=${group.domain}`
    }
  }
}
</script>

<style scoped>
.count {
  min-width: 130px;
}
.sortable-group {
  border: 1px solid #007bff;
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
