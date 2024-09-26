<template>
  <div v-if="!contextStore.loading" class="default-margins">
    <CohortPageHeader :is-cohort-history-page="true" />
    <div v-if="cohortStore.domain === 'admitted_students' && cohortStore.students">
      <AdmitDataWarning :updated-at="get(cohortStore.students, '[0].updatedAt')" />
    </div>
    <div v-if="totalEventsCount > itemsPerPage" class="pt-3">
      <Pagination
        :click-handler="goToPage"
        :init-page-number="currentPage"
        :limit="10"
        :per-page="itemsPerPage"
        :total-rows="totalEventsCount"
      />
      <hr />
    </div>
    <table
      v-if="!isEmpty(events)"
      id="cohort-history-table"
      class="w-100 mt-5"
    >
      <thead>
        <tr>
          <th class="pr-2 pb-2">Status</th>
          <th class="pr-2 pb-2 text-no-wrap">Change Date</th>
          <th class="pr-2 pb-2">Name</th>
          <th class="pr-2 pb-2">SID</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(event, index) in events" :key="index">
          <td class="pr-2 py-1 text-no-wrap">
            <div
              :id="`event-${index}-status`"
              class="pill-membership-change border-sm"
              :class="event.eventType === 'added' ? 'pill-added' : 'pill-removed'"
            >
              {{ event.eventType }}
            </div>
          </td>
          <td class="pr-2 py-1 text-no-wrap">
            <div :id="`event-${index}-date`">{{ DateTime.fromISO(event.createdAt).toLocaleString(DateTime.DATE_MED) }}</div>
          </td>
          <td class="pr-2 py-1 text-no-wrap">
            <router-link
              v-if="event.uid"
              :id="`event-${index}-student-name`"
              :class="{'demo-mode-blur': get(currentUser, 'inDemoMode')}"
              :to="studentRoutePath(event.uid, get(currentUser, 'inDemoMode'))"
            >
              <span v-html="lastNameFirst(event)" />
            </router-link>
            <div
              v-if="!event.uid"
              :id="`event-${index}-student-name-not-available`"
            >
              Not available
            </div>
          </td>
          <td class="pr-2 py-1 text-no-wrap">
            <div
              :id="`event-${index}-sid`"
              :class="{'demo-mode-blur': get(currentUser, 'inDemoMode')}"
            >
              {{ event.sid }}
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="totalEventsCount > itemsPerPage" class="pa-3">
      <hr />
      <Pagination
        :click-handler="goToPage"
        id-prefix="auxiliary-pagination"
        :init-page-number="currentPage"
        :is-widget-at-bottom-of-page="true"
        :limit="10"
        :per-page="itemsPerPage"
        :total-rows="totalEventsCount"
      />
    </div>
    <div v-if="isEmpty(events)" id="cohort-history-no-events" class="pt-3">
      This cohort has no history available.
    </div>
  </div>
</template>

<script setup>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning.vue'
import CohortPageHeader from '@/components/cohort/CohortPageHeader.vue'
import Pagination from '@/components/util/Pagination'
import {DateTime} from 'luxon'
import {get, isEmpty} from 'lodash'
import {getCohortEvents} from '@/api/cohort'
import {lastNameFirst, putFocusNextTick, studentRoutePath} from '@/lib/utils'
import {onMounted, ref} from 'vue'
import {scrollToTop} from '@/lib/utils'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {useContextStore} from '@/stores/context'

const cohortStore = useCohortStore()
const contextStore = useContextStore()

const currentPage = ref(1)
const currentUser = contextStore.currentUser
const events = ref([])
const itemsPerPage = ref(50)
const offset = ref(0)
const totalEventsCount = ref(0)

contextStore.loadingStart('Cohort history is loading')

onMounted(() => {
  goToPage(1)
})

const goToPage = page => {
  currentPage.value = page
  offset.value = (page - 1) * itemsPerPage.value
  contextStore.loadingStart()
  scrollToTop(10)
  getCohortEvents(cohortStore.cohortId, offset.value, itemsPerPage.value).then(data => {
    totalEventsCount.value = data.count
    events.value = data.events
    contextStore.loadingComplete('Cohort history has loaded')
    putFocusNextTick(page > 1 ? `pagination-page-${page}` : 'page-header')
  })
}
</script>

<style scoped>
.pill-membership-change {
  border-radius: 5px;
  display: inline-block;
  font-size: 12px;
  font-weight: 800;
  height: 28px;
  min-width: 80px;
  max-width: 80px;
  padding-top: 5px;
  text-align: center;
  text-transform: uppercase;
  white-space: nowrap;
}
.pill-added {
  background-color: rgb(var(--v-theme-light-blue));
  color: rgb(var(--v-theme-tertiary));
}
.pill-removed {
  background-color: rgb(var(--v-theme-pale-yellow));
  color: rgb(var(--v-theme-gold));
}
</style>
