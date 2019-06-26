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
              <font-awesome v-if="isFetching" icon="spinner" spin />
              <font-awesome v-if="!isFetching" :icon="isOpen ? 'caret-down' : 'caret-right'" />
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
        <div v-if="size(cohort.studentsWithAlerts) === 50" :id="`home-cohort-${cohort.id}-alert-limited`" class="m-3">
          Showing 50 students with a high number of alerts.
          <router-link :id="`home-cohort-${cohort.id}-alert-limited-view-all`" :to="`/cohort/${cohort.id}`">
            View all {{ cohort.totalStudentCount }} students in "{{ cohort.name }}"
          </router-link>
        </div>
        <SortableStudents :students="cohort.studentsWithAlerts" :options="getSortOptions(cohort)" />
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
import Context from '@/mixins/Context';
import HomeUtil from '@/components/home/HomeUtil';
import SortableStudents from '@/components/search/SortableStudents';
import store from '@/store';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'HomeCohort',
  components: {
    SortableStudents
  },
  mixins: [Context, HomeUtil, UserMetadata, Util],
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
            this.alertScreenReader(`Loaded students with alerts who are in cohort ${this.cohort.name}`);
            this.gaCohortEvent({
              id: this.cohort.id,
              name: this.cohort.name,
              action: 'Fetch students with alerts'
            });
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
