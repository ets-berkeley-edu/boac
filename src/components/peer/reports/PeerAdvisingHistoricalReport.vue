<template>
  <div>
    <v-btn
      id="show-hide-peer-note-count-by-month"
      aria-controls="peer-note-count-by-month"
      :aria-expanded="isExpanded"
      class="justify-start px-0 w-100"
      color="primary"
      variant="text"
      @click="onClickExpand"
    >
      <div class="align-center d-flex">
        <v-progress-circular
          v-if="isFetching"
          class="mr-2"
          :indeterminate="true"
          :size="16"
          :width="3"
          color="primary"
        />
        <v-icon
          v-if="!isFetching"
          :icon="isExpanded ? mdiMenuDown : mdiMenuRight"
          size="24"
        />
        <div class="d-flex flex-wrap">
          <span>BOA peer note count by month </span>
          <span class="text-medium-emphasis">(reverse chronological)</span>
        </div>
      </div>
    </v-btn>
    <v-expand-transition>
      <div v-if="isExpanded && report" id="peer-note-count-by-month" class="w-100">
        <div v-if="!report.length" class="font-italic py-2 text-medium-emphasis">
          The {{ peerAdvisingDepartment.name }} Peer Advising department created no notes prior to {{ currentMonthLabel }}.
        </div>
        <div v-if="report.length">
          <v-card
            v-for="(year, index) in report"
            :id="`peer-note-counts-year-${year.label}`"
            :key="index"
            :class="{'mt-1': index === 0, 'mt-3': index > 0}"
            class="rounded-lg v-card-border w-100"
            flat
          >
            <v-card-title class="bg-primary font-size-14">
              {{ year.label }}
            </v-card-title>
            <v-card-text>
              <div
                v-for="month in year.months"
                :key="month.label"
                class="mt-2"
              >
                <div class="align-center d-flex justify-space-between pb-2">
                  <div class="font-weight-bold">
                    {{ month.label }}
                  </div>
                  <div class="pr-1 text-right">
                    <PillCount
                      :id="`peer-note-count-${toLower(month.label)}-${year.label}`"
                      class="px-2 sidebar-pill text-white"
                      color="primary"
                    >
                      <span class="font-size-14">{{ month.noteCount }}</span>
                    </PillCount>
                  </div>
                </div>
                <table :id="`peer-advisors-${toLower(month.label)}-${year.label}`" class="border-sm w-100">
                  <thead>
                    <tr>
                      <th
                        :aria-sort="getPeerAdvisorAriaSort('name', getSortOptions(`${toLower(month.label)}-${year.label}`))"
                        class="bg-grey-lighten-2 border-sm font-size-12 w-90"
                        scope="col"
                      >
                        <v-btn
                          :id="`sort-peer-advisors-by-name-${toLower(month.label)}-${year.label}`"
                          :append-icon="getSortOptions(`${toLower(month.label)}-${year.label}`).sortBy === 'name' ? (getSortOptions(`${toLower(month.label)}-${year.label}`).sortDesc ? mdiMenuDown : mdiMenuUp) : undefined"
                          aria-label="Sort by Peer Advisor"
                          block
                          class="sort-col-btn font-weight-bold text-no-wrap v-table-sort-btn-override"
                          :class="{'icon-visible': getSortOptions(`${toLower(month.label)}-${year.label}`).sortBy === 'name'}"
                          color="body"
                          density="compact"
                          size="small"
                          text="Peer Advisor"
                          variant="plain"
                          @click="onSortName(`${toLower(month.label)}-${year.label}`)"
                        />
                      </th>
                      <th
                        :aria-sort="getPeerAdvisorAriaSort('noteCount', getSortOptions(`${toLower(month.label)}-${year.label}`))"
                        class="bg-grey-lighten-2 border-sm font-size-12 text-right"
                        scope="col"
                      >
                        <v-btn
                          :id="`sort-peer-advisors-by-note-count-${toLower(month.label)}-${year.label}`"
                          :append-icon="getSortOptions(`${toLower(month.label)}-${year.label}`).sortBy === 'noteCount' ? (getSortOptions(`${toLower(month.label)}-${year.label}`).sortDesc ? mdiMenuDown : mdiMenuUp) : undefined"
                          aria-label="Sort by Notes"
                          block
                          class="sort-col-btn font-weight-bold justify-end ml-auto text-no-wrap v-table-sort-btn-override"
                          :class="{'icon-visible': getSortOptions(`${toLower(month.label)}-${year.label}`).sortBy === 'noteCount'}"
                          color="body"
                          density="compact"
                          size="small"
                          text="Notes"
                          variant="plain"
                          @click="onSortNoteCount(`${toLower(month.label)}-${year.label}`)"
                        />
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="peerAdvisor in sortPeerAdvisors(month.peerAdvisors, getSortOptions(`${toLower(month.label)}-${year.label}`))" :key="peerAdvisor.uid">
                      <td
                        :id="`peer-advisor-${peerAdvisor.uid}-during-${toLower(month.label)}-${year.label}`"
                        :class="{
                          'demo-mode-blur': currentUser.inDemoMode,
                          'font-weight-medium text-red': peerAdvisor.deletedAt
                        }"
                        class="border-sm w-90"
                      >
                        {{ peerAdvisor.name }}
                        <span v-if="peerAdvisor.deletedAt" class="text-medium-emphasis">
                          (deleted on <Date :id="`peer-advisor-${peerAdvisor.uid}-deleted-at`" :date="peerAdvisor.deletedAt" />)
                        </span>
                      </td>
                      <td
                        :class="{'font-weight-medium text-red': peerAdvisor.deletedAt}"
                        class="border-sm text-no-wrap text-right"
                      >
                        <NotesCreatedByPeerAdvisor
                          v-if="get(peerAdvisor, 'noteCount')"
                          :header-text="`${pluralize('note', toInt(get(peerAdvisor, 'noteCount') || 0), {1: 'One'})} created by ${currentUser.inDemoMode ? '...' : peerAdvisor.name}`"
                          :peer-advising-department="peerAdvisingDepartment"
                          :timeframe="month"
                          :user="peerAdvisor"
                        />
                        <span v-if="!get(peerAdvisor, 'noteCount')">0</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </div>
    </v-expand-transition>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {get, isNil, toLower} from 'lodash'
import {mdiMenuDown, mdiMenuRight, mdiMenuUp} from '@mdi/js'
import {ref} from 'vue'
import type {PeerAdvisingDepartment} from '@/lib/types'
import type {PeerAdvisingHistoricalReport} from '@/lib/types-peer-advising'
import Date from '@/components/util/Date.vue'
import NotesCreatedByPeerAdvisor from '@/components/peer/note/NotesCreatedByPeerAdvisor.vue'
import PillCount from '@/components/util/PillCount.vue'
import {getPeerAdvisingHistoricalReport} from '@/api/peer-advising-reports'
import {
  defaultPeerAdvisorSortOptions,
  getPeerAdvisorAriaSort,
  sortPeerAdvisors,
  togglePeerAdvisorSort
} from '@/lib/peer-advisor-sort'
import type {PeerAdvisorSortOptions} from '@/lib/peer-advisor-sort'
import {pluralize, toInt} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  currentMonthLabel: {
    required: true,
    type: String
  },
  peerAdvisingDepartment: {
    required: true,
    type: Object as PropType<PeerAdvisingDepartment>
  }
})

const currentUser = useContextStore().currentUser
const isExpanded = ref(false)
const isFetching = ref(false)
const report = ref<PeerAdvisingHistoricalReport | undefined>()
const sortOptionsByTable = ref<Record<string, PeerAdvisorSortOptions>>({})

const getSortOptions = (tableKey: string): PeerAdvisorSortOptions => {
  return sortOptionsByTable.value[tableKey] || defaultPeerAdvisorSortOptions()
}

const onSortName = (tableKey: string) => {
  sortOptionsByTable.value = {
    ...sortOptionsByTable.value,
    [tableKey]: togglePeerAdvisorSort('name', getSortOptions(tableKey))
  }
}

const onSortNoteCount = (tableKey: string) => {
  sortOptionsByTable.value = {
    ...sortOptionsByTable.value,
    [tableKey]: togglePeerAdvisorSort('noteCount', getSortOptions(tableKey))
  }
}

const onClickExpand = () => {
  const requiresLazyLoad = isNil(report.value)
  const done = () => isExpanded.value = !isExpanded.value
  if (requiresLazyLoad) {
    isFetching.value = true
    getPeerAdvisingHistoricalReport(props.peerAdvisingDepartment.id).then(data => {
      report.value = data
      isFetching.value = false
      done()
    })
  } else {
    done()
  }
}
</script>

<style scoped>
table {
  border: 1px solid;
  border-collapse: collapse;
}
th {
  border: 1px solid;
  font-size: 14px;
  padding: 6px 12px;
}
td {
  border: 1px solid;
  padding: 6px 12px;
}
.sort-col-btn {
  height: 28px !important;
  letter-spacing: normal !important;
  margin: 0 4px 0 -.1em;
  min-width: 0px !important;
  padding: 0 2px 0 4px;
}
.v-card-border {
  border: 1px solid rgb(var(--v-theme-primary));
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
