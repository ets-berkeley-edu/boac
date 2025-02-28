<template>
  <div class="default-margins">
    <table
      v-if="!isEmpty(notes)"
      id="cohort-history-table"
      class="w-100 mt-5"
    >
      <thead>
        <tr>
          <th class="pb-2 pr-2">Student</th>
          <th class="pb-2 pr-2">Note</th>
          <th class="pb-2 pr-2">Topics</th>
          <th class="pb-2 pr-2 text-no-wrap">Date Created</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(note, index) in notes" :key="index">
          <td class="pr-2 py-1 text-no-wrap">
            <div
              :id="`note-${index}-student`"
              :class="{'demo-mode-blur': currentUser.inDemoMode}"
              class="border-sm"
            >
              {{ note.sid }}
            </div>
          </td>
          <td :id="`note-body-in-row-${index}`">
            {{ note.body }}
          </td>
          <td :id="`note-body-in-row-${index}`">
            <router-link
              v-if="note.sid"
              :id="`note-${index}-student-name`"
              :class="{'demo-mode-blur': currentUser.inDemoMode}"
              :to="studentRoutePath(note.sid, currentUser.inDemoMode)"
            >
              <span v-html="lastNameFirst(note)" />
            </router-link>
            <div
              v-if="!note.sid"
              :id="`note-${index}-student-name-not-available`"
            >
              Not available
            </div>
          </td>
          <td :id="`note-created-date-in-row-${index}`" class="pr-2 py-1 text-no-wrap">
            {{ DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_MED) }}
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="totalNoteCount > itemsPerPage" class="pa-3">
      <hr />
      <Pagination
        :click-handler="goToPage"
        id-prefix="auxiliary-pagination"
        :init-page-number="currentPage"
        :is-widget-at-bottom-of-page="true"
        :limit="10"
        :per-page="itemsPerPage"
        :total-rows="totalNoteCount"
      />
    </div>
    <div v-if="isEmpty(notes)" id="peer-advisor-no-notes" class="pt-3">
      This cohort has no history available.
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {DateTime} from 'luxon'
import {isEmpty} from 'lodash'
import type {Note} from '@/lib/types'
import Pagination from '@/components/util/Pagination.vue'
import {lastNameFirst, studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

defineProps({
  currentPage: {
    required: true,
    type: Number
  },
  goToPage: {
    required: true,
    type: Function
  },
  itemsPerPage: {
    required: true,
    type: Number
  },
  notes: {
    required: true,
    type: Array as PropType<Note[]>
  },
  totalNoteCount: {
    required: true,
    type: Number
  },
})

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
</script>

<style scoped>
</style>
