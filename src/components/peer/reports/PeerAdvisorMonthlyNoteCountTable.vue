<template>
  <div v-if="peerAdvisors.length" :class="{'mt-3': addTopMargin}">
    <div class="font-size-14 font-weight-bold mb-1">
      {{ sectionLabel }}
    </div>
    <table :id="`peer-advisors-${idPrefix}`" class="border-sm w-100">
      <thead>
        <tr>
          <th
            :aria-sort="getPeerAdvisorAriaSort('name', sortOptions)"
            :class="headerClass"
            class="bg-grey-lighten-2 border-sm w-90"
            scope="col"
          >
            <v-btn
              :id="`sort-${idPrefix}-peer-advisors-by-name`"
              :append-icon="sortOptions.sortBy === 'name' ? (sortOptions.sortDesc ? mdiMenuDown : mdiMenuUp) : undefined"
              aria-label="Sort by Peer Advisor"
              block
              class="sort-col-btn font-weight-bold text-no-wrap v-table-sort-btn-override"
              :class="{'icon-visible': sortOptions.sortBy === 'name'}"
              color="body"
              density="compact"
              size="small"
              text="Peer Advisor"
              variant="plain"
              @click="emit('sort-name')"
            />
          </th>
          <th
            :aria-sort="getPeerAdvisorAriaSort('noteCount', sortOptions)"
            :class="headerClass"
            class="bg-grey-lighten-2 border-sm text-right"
            scope="col"
          >
            <v-btn
              :id="`sort-${idPrefix}-peer-advisors-by-note-count`"
              :append-icon="sortOptions.sortBy === 'noteCount' ? (sortOptions.sortDesc ? mdiMenuDown : mdiMenuUp) : undefined"
              aria-label="Sort by Notes"
              block
              class="sort-col-btn font-weight-bold justify-end ml-auto text-no-wrap v-table-sort-btn-override"
              :class="{'icon-visible': sortOptions.sortBy === 'noteCount'}"
              color="body"
              density="compact"
              size="small"
              text="Notes"
              variant="plain"
              @click="emit('sort-note-count')"
            />
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="peerAdvisor in sortedPeerAdvisors"
          :id="`tr-${idPrefix}-peer-advisor-${peerAdvisor.uid}`"
          :key="peerAdvisor.uid"
        >
          <td
            :id="`td-${idPrefix}-peer-advisor-${peerAdvisor.uid}-name`"
            :class="{
              'demo-mode-blur': currentUser.inDemoMode,
              'font-weight-medium text-red': isDeletedSection && !currentUser.inDemoMode
            }"
            class="border-sm w-90"
          >
            {{ peerAdvisor.name }}
            <span v-if="isDeletedSection && peerAdvisor.deletedAt" class="text-medium-emphasis">
              (deleted on <Date :id="`peer-advisor-${peerAdvisor.uid}-deleted-at`" :date="peerAdvisor.deletedAt" />)
            </span>
          </td>
          <td
            :id="`td-${idPrefix}-peer-advisor-${peerAdvisor.uid}-note-count`"
            class="border-sm text-no-wrap text-right"
          >
            <NotesCreatedByPeerAdvisor
              v-if="get(peerAdvisor, 'noteCount')"
              :header-text="`${pluralize('note', toInt(get(peerAdvisor, 'noteCount') || 0), {1: 'One'})} created by ${currentUser.inDemoMode ? '...' : peerAdvisor.name}`"
              :peer-advising-department="peerAdvisingDepartment"
              :timeframe="timeframe"
              :user="peerAdvisor"
            />
            <span
              v-if="!get(peerAdvisor, 'noteCount')"
              :class="{'font-weight-medium text-red': isDeletedSection}"
            >
              0<span class="sr-only"> notes created in {{ timeframe.label }}</span>
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {computed} from 'vue'
import {get} from 'lodash'
import {mdiMenuDown, mdiMenuUp} from '@mdi/js'
import type {PeerAdvisingDepartment} from '@/lib/types'
import type {Month, PeerAdvisorNoteCount} from '@/lib/types-peer-advising'
import Date from '@/components/util/Date.vue'
import NotesCreatedByPeerAdvisor from '@/components/peer/note/NotesCreatedByPeerAdvisor.vue'
import {
  getPeerAdvisorAriaSort,
  sortPeerAdvisors
} from '@/lib/peer-advisor-sort'
import type {PeerAdvisorSortOptions} from '@/lib/peer-advisor-sort'
import {pluralize, toInt} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  addTopMargin: {
    type: Boolean
  },
  headerClass: {
    default: '',
    type: String
  },
  idPrefix: {
    required: true,
    type: String
  },
  isDeletedSection: {
    type: Boolean
  },
  peerAdvisors: {
    required: true,
    type: Array as PropType<PeerAdvisorNoteCount[]>
  },
  peerAdvisingDepartment: {
    required: true,
    type: Object as PropType<PeerAdvisingDepartment>
  },
  sectionLabel: {
    required: true,
    type: String
  },
  sortOptions: {
    required: true,
    type: Object as PropType<PeerAdvisorSortOptions>
  },
  timeframe: {
    required: true,
    type: Object as PropType<Month>
  }
})

const emit = defineEmits<{
  'sort-name': [],
  'sort-note-count': []
}>()

const currentUser = useContextStore().currentUser

const sortedPeerAdvisors = computed(() => {
  return sortPeerAdvisors(props.peerAdvisors, props.sortOptions)
})
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
