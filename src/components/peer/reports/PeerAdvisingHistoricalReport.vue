<template>
  <div>
    <v-btn
      id="show-hide-personal-details"
      aria-controls="peer-note-count-by-month"
      :aria-expanded="isExpanded"
      class="text-no-wrap"
      color="primary"
      variant="text"
      @click="() => isExpanded = !isExpanded"
    >
      <div class="align-center d-flex">
        <v-icon :icon="isExpanded ? mdiMenuDown : mdiMenuRight" size="24" />
        <div>
          BOA peer note count by month
          <span class="text-medium-emphasis">(reverse chronological)</span>
        </div>
      </div>
    </v-btn>
    <v-expand-transition>
      <div v-show="isExpanded">
        <v-card
          v-for="year in notesReport.historical.years"
          :id="`peer-note-counts-year-${year.label}`"
          :key="year.label"
          class="bg-sky-blue"
          flat
        >
          <v-card-title>{{ year.label }}</v-card-title>
          <v-card-text>
            <div v-for="(month, index) in year.months" :key="index">
              <div class="d-flex justify-space-between">
                <div>
                  {{ month.label }}
                </div>
                <div>
                  {{ month.totalNoteCount }}
                </div>
              </div>
              <table class="border-sm w-100">
                <thead>
                  <tr>
                    <th class="bg-grey-lighten-2 border-sm w-90">Peer Advisor</th>
                    <th class="bg-grey-lighten-2 border-sm text-right">Notes</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="peerAdvisor in month.peerAdvisors" :key="peerAdvisor.id">
                    <td class="border-sm w-90">{{ peerAdvisor.name }}</td>
                    <td class="border-sm text-no-wrap text-right">
                      <NotesCreatedByPeerAdvisor
                        v-if="get(peerAdvisor, 'noteCount')"
                        :header-text="`${pluralize('note', toInt(get(peerAdvisor, 'noteCount') || 0))} created by ${peerAdvisor.name}`"
                        :peer-advising-department-id="notesReport.peerAdvisingDepartment.id"
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
    </v-expand-transition>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {get} from 'lodash'
import {mdiMenuDown, mdiMenuRight} from '@mdi/js'
import {ref} from 'vue'
import type {PeerAdvisingManagerReport} from '@/lib/types'
import NotesCreatedByPeerAdvisor from '@/components/peer/note/NotesCreatedByPeerAdvisor.vue'
import {pluralize, toInt} from '@/lib/utils'

defineProps({
  notesReport: {
    required: true,
    type: Object as PropType<PeerAdvisingManagerReport>
  }
})

const isExpanded = ref(false)
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
</style>
