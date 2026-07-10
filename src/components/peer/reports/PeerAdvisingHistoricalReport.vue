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
                <PeerAdvisorMonthlyNoteCountTable
                  :id-prefix="`${monthTableKey(month, year.label)}-active`"
                  header-class="font-size-12"
                  :peer-advisors="partitionPeerAdvisors(month.peerAdvisors).active"
                  :peer-advising-department="peerAdvisingDepartment"
                  section-label="Active Peer Advisors"
                  :sort-options="getSortOptions(`${monthTableKey(month, year.label)}-active`)"
                  :timeframe="month"
                  @sort-name="onSortName(`${monthTableKey(month, year.label)}-active`)"
                  @sort-note-count="onSortNoteCount(`${monthTableKey(month, year.label)}-active`)"
                />
                <PeerAdvisorMonthlyNoteCountTable
                  :id-prefix="`${monthTableKey(month, year.label)}-deleted`"
                  :add-top-margin="true"
                  header-class="font-size-12"
                  :is-deleted-section="true"
                  :peer-advisors="partitionPeerAdvisors(month.peerAdvisors).deleted"
                  :peer-advising-department="peerAdvisingDepartment"
                  section-label="Deleted Peer Advisors"
                  :sort-options="getSortOptions(`${monthTableKey(month, year.label)}-deleted`)"
                  :timeframe="month"
                  @sort-name="onSortName(`${monthTableKey(month, year.label)}-deleted`)"
                  @sort-note-count="onSortNoteCount(`${monthTableKey(month, year.label)}-deleted`)"
                />
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
import {isNil, toLower} from 'lodash'
import {mdiMenuDown, mdiMenuRight} from '@mdi/js'
import {ref} from 'vue'
import type {PeerAdvisingDepartment} from '@/lib/types'
import type {PeerAdvisingHistoricalReport, PeerAdvisingReportTimeframe} from '@/lib/types-peer-advising'
import PeerAdvisorMonthlyNoteCountTable from '@/components/peer/reports/PeerAdvisorMonthlyNoteCountTable.vue'
import PillCount from '@/components/util/PillCount.vue'
import {getPeerAdvisingHistoricalReport} from '@/api/peer-advising-reports'
import {
  defaultPeerAdvisorNameSortOptions,
  partitionPeerAdvisors,
  togglePeerAdvisorSort
} from '@/lib/peer-advisor-sort'
import type {PeerAdvisorSortOptions} from '@/lib/peer-advisor-sort'

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

const isExpanded = ref(false)
const isFetching = ref(false)
const report = ref<PeerAdvisingHistoricalReport | undefined>()
const sortOptionsByTable = ref<Record<string, PeerAdvisorSortOptions>>({})

const getSortOptions = (tableKey: string): PeerAdvisorSortOptions => {
  return sortOptionsByTable.value[tableKey] || defaultPeerAdvisorNameSortOptions()
}

const monthTableKey = (month: PeerAdvisingReportTimeframe, yearLabel: string | number) => {
  return `${toLower(month.label)}-${yearLabel}`
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
.v-card-border {
  border: 1px solid rgb(var(--v-theme-primary));
}
</style>
