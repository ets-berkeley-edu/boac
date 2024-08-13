<template>
  <div>
    <SectionSpinner :loading="loading" />
    <div v-if="!loading && totalEventsCount > itemsPerPage" class="pt-3">
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
      v-if="!loading && !isEmpty(events)"
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
              class="pill-membership-change"
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
    <div v-if="!loading && totalEventsCount > itemsPerPage" class="pa-3">
      <hr />
      <Pagination
        :click-handler="goToPage"
        id-prefix="auxiliary-pagination"
        :init-page-number="currentPage"
        :limit="10"
        :per-page="itemsPerPage"
        :total-rows="totalEventsCount"
      />
    </div>
    <div v-if="!loading && isEmpty(events)" id="cohort-history-no-events" class="pt-3">
      This cohort has no history available.
    </div>
  </div>
</template>

<script setup>
import Pagination from '@/components/util/Pagination'
import SectionSpinner from '@/components/util/SectionSpinner'
import {DateTime} from 'luxon'
import {alertScreenReader, scrollToTop} from '@/lib/utils'
import {get, isEmpty} from 'lodash'
import {getCohortEvents} from '@/api/cohort'
import {lastNameFirst, studentRoutePath} from '@/lib/utils'
import {onMounted, ref} from 'vue'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {useContextStore} from '@/stores/context'

const cohortStore = useCohortStore()
const contextStore = useContextStore()
const currentPage = ref(1)
const currentUser = contextStore.currentUser
const events = ref([])
const itemsPerPage = ref(50)
const loading = ref(false)
const offset = ref(0)
const totalEventsCount = ref(0)

onMounted(() => {
  goToPage(1)
})

const goToPage = page => {
  currentPage.value = page
  offset.value = (page - 1) * itemsPerPage.value
  loadEvents()
}

const loadEvents = () => {
  loading.value = true
  alertScreenReader('Cohort history is loading')
  scrollToTop(10)
  getCohortEvents(cohortStore.cohortId, offset.value, itemsPerPage.value).then(data => {
    totalEventsCount.value = data.count
    events.value = data.events
    loading.value = false
    alertScreenReader('Cohort history has loaded')
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
  padding-top: 6px;
  text-align: center;
  text-transform: uppercase;
  white-space: nowrap;
}
.pill-added {
  background-color: rgb(var(--v-theme-light-blue));
  color: rgb(var(--v-theme-tertiary));
}
.pill-removed {
  background-color: rgb(var(--v-theme-light-yellow));
  color: rgb(var(--v-theme-gold));
}
</style>
