<template>
  <div
    :id="`home-cohort-${cohort.id}`"
    class="accordion panel"
    :class="{'panel-open': cohort.isOpen}">
    <div class="panel-heading">
      <a
        :id="`home-cohort-${cohort.id}-toggle`"
        v-b-toggle="`home-cohort-${cohort.id}`"
        class="accordion-heading-link"
        tabindex="0"
        role="button"
        href="#"
        @click.prevent="fetchStudents()">
        <div class="accordion-heading">
          <div class="accordion-heading-name">
            <div class="accordion-heading-caret">
              <i
                :id="`home-cohort-${cohort.id}-caret`"
                :aria-label="isFetching ? 'Loading cohort details' : ''"
                :class="{
                  'fas fa-spinner fa-spin': isFetching,
                  'fas fa-caret-right': !isOpen,
                  'fas fa-caret-down': isOpen
                }"></i>
            </div>
            <h2 class="page-section-header-sub accordion-header">
              <span class="sr-only">{{ `${isOpen ? 'Hide' : 'Show'} details for cohort ` }}</span>
              <span>{{ cohort.name }}</span>
              (<span :id="`home-cohort-${cohort.id}-total-student-count`">{{ cohort.totalStudentCount }}</span>
              <span class="sr-only">&nbsp;students</span>)
            </h2>
          </div>
          <div class="accordion-heading-count">
            <div class="sortable-table-header accordion-heading-count-label">
              Total Issues:
            </div>
            <div
              v-if="!cohort.alertCount"
              class="home-issues-pill home-issues-pill-zero"
              aria-label="`No issues for ${cohort.name}`">0</div>
            <div
              v-if="cohort.alertCount"
              class="home-issues-pill home-issues-pill-nonzero"
              aria-label="`${cohort.alertCount} alerts for ${cohort.name}`">{{ cohort.alertCount }}</div>
          </div>
        </div>
      </a>
    </div>
    <b-collapse
      :id="`home-cohort-${cohort.id}`"
      :aria-expanded="isOpen"
      class="panel-body pr-3"
      :class="{'panel-open': isOpen}">
      <div v-if="cohort.studentsWithAlerts && size(cohort.studentsWithAlerts)">
        <div v-if="size(cohort.studentsWithAlerts) == 50" class="m-3" :id="`home-cohort-${cohort.id}-alert-limited`">
          Showing 50 students with the most alerts.
          <router-link :id="`home-cohort-${cohort.id}-alert-limited-view-all`" :to="`/cohort/${cohort.id}`">
            View all {{ cohort.totalStudentCount }} students in "{{ cohort.name }}"
          </router-link>
        </div>
        <SortableStudents :students="cohort.studentsWithAlerts" />
      </div>
      <div>
        <router-link :id="`home-cohort-${cohort.id}-view-all`" :to="`/cohort/${cohort.id}`">
          <span v-if="cohort.totalStudentCount">
            View <span>{{ 'student' | pluralize(cohort.totalStudentCount,
                                                {1: 'the one', 'other': `all ${cohort.totalStudentCount}`}) }}
            </span>
            in "<span>{{ cohort.name }}</span>"
          </span>
          <span v-if="!cohort.totalStudentCount">
            "<span>{{ cohort.name }}</span>" has 0 students
          </span>
        </router-link>
      </div>
    </b-collapse>
  </div>
</template>

<script>
import GoogleAnalytics from '@/mixins/GoogleAnalytics';
import SortableStudents from '@/components/search/SortableStudents';
import store from '@/store';
import Util from '@/mixins/Util';

export default {
  name: 'HomeCohort',
  components: {
    SortableStudents
  },
  mixins: [GoogleAnalytics, Util],
  props: {
    cohort: Object
  },
  data: () => ({
    isOpen: false,
    isFetching: false
  }),
  methods: {
    fetchStudents() {
      this.isOpen = !this.isOpen;
      if (!this.isFetching) {
        this.isFetching = true;
        store
          .dispatch('cohort/loadStudentsWithAlerts', this.cohort.id)
          .then(cohort => {
            this.cohort = cohort;
            this.isFetching = false;
            this.gaEvent(
              'Home',
              'Fetch students with alerts',
              `Cohort: ${this.cohort.name}`,
              this.cohort.id
            );
          });
      }
    }
  }
};
</script>

<style scoped>
.panel-group .panel + .panel {
  margin-top: 5px;
}
.panel-heading {
  padding: 10px 15px 10px 0;
  border-top-left-radius: 3px;
  border-top-right-radius: 3px;
}
</style>
