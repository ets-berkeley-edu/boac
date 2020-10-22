<template>
  <div>
    <SectionSpinner :loading="loading" name="History" />
    <div v-if="!loading && totalEventsCount > itemsPerPage">
      <div class="pt-3">
        <Pagination
          :click-handler="goToPage"
          :init-page-number="currentPage"
          :limit="10"
          :per-page="itemsPerPage"
          :total-rows="totalEventsCount" />
      </div>
      <hr class="filters-section-separator " />
    </div>
    <b-table-simple
      v-if="!loading && !isEmpty(events)"
      id="cohort-history-table"
      class="cohort-history-table mt-3"
      :borderless="true">
      <b-thead>
        <b-tr>
          <b-th class="p-1 pb-2 sortable-table-header">Status</b-th>
          <b-th class="p-1 pb-2 sortable-table-header">Change Date</b-th>
          <b-th class="p-1 pb-2 sortable-table-header">Name</b-th>
          <b-th class="p-1 pb-2 sortable-table-header">SID</b-th>
        </b-tr>
      </b-thead>
      <b-tbody>
        <b-tr v-for="(event, index) in events" :key="index">
          <b-td class="p-1">
            <div
              :id="`event-${index}-status`"
              class="pill-membership-change"
              :class="event.eventType === 'added' ? 'pill-added' : 'pill-removed'">
              {{ event.eventType }}
            </div>
          </b-td>
          <b-td class="p-1">
            <div :id="`event-${index}-date`">{{ event.createdAt | moment('MMM D, YYYY') }}</div>
          </b-td>
          <b-td class="p-1">
            <router-link
              v-if="event.uid"
              :id="`event-${index}-student-name`"
              :aria-label="`Go to profile page of ${event.firstName} ${event.lastName}`"
              :class="{'demo-mode-blur': $currentUser.inDemoMode}"
              :to="studentRoutePath(event.uid, $currentUser.inDemoMode)"
              v-html="`${event.lastName}, ${event.firstName}`"></router-link>
            <div
              v-if="!event.uid"
              :id="`event-${index}-student-name-not-available`">
              Not available
            </div>
          </b-td>
          <b-td class="p-1">
            <div
              :id="`event-${index}-sid`"
              :class="{'demo-mode-blur': $currentUser.inDemoMode}">
              {{ event.sid }}
            </div>
          </b-td>
        </b-tr>
      </b-tbody>
    </b-table-simple>
    <div v-if="!loading && totalEventsCount > itemsPerPage" class="p-3">
      <Pagination
        :click-handler="goToPage"
        :init-page-number="currentPage"
        :limit="10"
        :per-page="itemsPerPage"
        :total-rows="totalEventsCount" />
    </div>
    <div v-if="!loading && isEmpty(events)" id="cohort-history-no-events" class="mt-3">
      This cohort has no history available.
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession'
import Context from '@/mixins/Context'
import Pagination from '@/components/util/Pagination'
import Scrollable from '@/mixins/Scrollable'
import SectionSpinner from '@/components/util/SectionSpinner'
import Util from '@/mixins/Util'
import { getCohortEvents } from '@/api/cohort'

export default {
  name: 'CohortHistory',
  components: {
    Pagination,
    SectionSpinner
  },
  mixins: [CohortEditSession, Context, Scrollable, Util],
  data: () => ({
    currentPage: 1,
    events: [],
    itemsPerPage: 50,
    offset: 0,
    loading: false,
    totalEventsCount: 0
  }),
  created() {
    this.goToPage(1)
  },
  methods: {
    goToPage(page) {
      this.currentPage = page
      this.offset = (page - 1) * this.itemsPerPage
      this.loadEvents()
    },
    loadEvents() {
      this.loading = true
      this.scrollToTop(10)
      getCohortEvents(this.cohortId, this.offset, this.itemsPerPage).then((response) => {
        this.totalEventsCount = response.count
        this.events = response.events
        this.loading = false
      })
    }
  },
}
</script>

<style scoped>
.cohort-history-table {
  max-width: 700px;
}
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
  whitespace: nowrap;
}
.pill-added {
  background-color: #c0ecff;
  color: #285d8b;
}
.pill-removed {
  background-color: #ffecc0;
  color: #857103;
}
</style>
