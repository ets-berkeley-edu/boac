<template>
  <div>
    <v-btn
      id="show-hide-personal-details"
      aria-controls="peer-note-count-by-month"
      :aria-expanded="isExpanded"
      class="text-no-wrap"
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
        <div>
          BOA peer note count by month
          <span class="text-medium-emphasis">(reverse chronological)</span>
        </div>
      </div>
    </v-btn>
    <v-expand-transition>
      <div v-if="isExpanded && report">
        <div v-if="!report.length" class="font-italic pl-6 pr-16 py-2 text-medium-emphasis">
          The {{ peerAdvisingDepartment.name }} Peer Advising department created no notes prior to {{ currentMonthLabel }}.
        </div>
        <div v-if="report.length">
          <v-card
            v-for="(year, index) in report"
            :id="`peer-note-counts-year-${year.label}`"
            :key="index"
            :class="{'mt-1': index === 0, 'mt-3': index > 0}"
            class="ml-2 rounded-lg v-card-border"
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
                      class="pa-2 sidebar-pill text-white"
                      color="primary"
                    >
                      <span class="font-size-14">{{ month.noteCount }}</span>
                    </PillCount>
                  </div>
                </div>
                <table :id="`peer-advisors-${toLower(month.label)}-${year.label}`" class="border-sm w-100">
                  <thead>
                    <tr>
                      <th class="bg-grey-lighten-2 border-sm font-size-12 w-90">Peer Advisor</th>
                      <th class="bg-grey-lighten-2 border-sm font-size-12 text-right">Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="peerAdvisor in month.peerAdvisors" :key="peerAdvisor.uid">
                      <td
                        :id="`peer-advisor-${peerAdvisor.uid}-during-${toLower(month.label)}-${year.label}`"
                        class="border-sm w-90"
                      >
                        {{ peerAdvisor.name }}
                      </td>
                      <td class="border-sm text-no-wrap text-right">
                        <NotesCreatedByPeerAdvisor
                          v-if="get(peerAdvisor, 'noteCount')"
                          :header-text="`${pluralize('note', toInt(get(peerAdvisor, 'noteCount') || 0))} created by ${peerAdvisor.name}`"
                          :peer-advising-department="peerAdvisingDepartment"
                          :user="peerAdvisor"
                        />
                        <span v-if="!get(peerAdvisor, 'noteCount')" :class="{'font-weight-medium text-red': peerAdvisor.deletedAt}">0</span>
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
import {mdiMenuDown, mdiMenuRight} from '@mdi/js'
import {ref} from 'vue'
import type {PeerAdvisingDepartment, PeerAdvisingHistoricalReport} from '@/lib/types'
import NotesCreatedByPeerAdvisor from '@/components/peer/note/NotesCreatedByPeerAdvisor.vue'
import PillCount from '@/components/util/PillCount.vue'
import {getPeerAdvisingHistoricalReport} from '@/api/peer-advising-reports'
import {pluralize, toInt} from '@/lib/utils'

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
#show-hide-personal-details {
  margin-left: -16px;
}
.v-card-border {
  border: 1px solid rgb(var(--v-theme-primary));
}
</style>
