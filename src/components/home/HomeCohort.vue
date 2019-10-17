<template>
  <div
    :id="`home-cohort-${cohort.id}`"
    class="accordion panel"
    :class="{'panel-open': cohort.isOpen}">
    <div class="panel-heading" :class="{'compact-background mt-2 p-0': compact}">
      <a
        :id="`home-cohort-${cohort.id}-toggle`"
        v-b-toggle="`home-cohort-${cohort.id}`"
        class="accordion-heading-link"
        tabindex="0"
        role="button"
        href="#"
        @click.prevent="fetchStudents()">
        <div class="accordion-heading" :class="{'compact-header': compact}">
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
            <div v-if="!compact" class="sortable-table-header accordion-heading-count-label">
              Total Issues:
            </div>
            <div
              v-if="!cohort.alertCount"
              class="pill-alerts-home pill-alerts-home-zero"
              aria-label="`No issues for ${cohort.name}`">0</div>
            <div
              v-if="cohort.alertCount"
              class="font-weight-normal pill-alerts-home pill-alerts-home-nonzero pl-2 pr-2"
              aria-label="`${cohort.alertCount} alerts for ${cohort.name}`">{{ cohort.alertCount }}</div>
          </div>
        </div>
      </a>
    </div>
    <b-collapse
      :id="`home-cohort-${cohort.id}`"
      :aria-expanded="isOpen"
      class="panel-body pr-3"
      :class="{'panel-open': isOpen, 'compact-background': compact}">
      <div v-if="cohort.studentsWithAlerts && size(cohort.studentsWithAlerts)">
        <div v-if="!compact && size(cohort.studentsWithAlerts) === 50" :id="`home-cohort-${cohort.id}-alert-limited`" class="m-3">
          Showing 50 students with a high number of alerts.
          <router-link :id="`home-cohort-${cohort.id}-alert-limited-view-all`" :to="`/cohort/${cohort.id}`">
            View all {{ cohort.totalStudentCount }} students in "{{ cohort.name }}"
          </router-link>
        </div>
        <SortableStudents
          :students="cohort.studentsWithAlerts"
          :options="sortableStudentsOptions(cohort, compact)" />
      </div>
      <div class="pl-3 pb-3">
        <router-link :id="`home-cohort-${cohort.id}-view-all`" :to="`/cohort/${cohort.id}`">
          <span v-if="cohort.totalStudentCount">
            View <span>{{ 'student' | pluralize(cohort.totalStudentCount, {1: 'the one', 'other': `all ${cohort.totalStudentCount}`}) }}</span>
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
import Berkeley from '@/mixins/Berkeley';
import Context from '@/mixins/Context';
import SortableStudents from '@/components/search/SortableStudents';
import store from '@/store';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'HomeCohort',
  components: {
    SortableStudents
  },
  mixins: [Berkeley, Context, UserMetadata, Util],
  props: {
    cohort: {
      required: true,
      type: Object
    },
    compact: {
      default: false,
      type: Boolean
    }
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
.compact-background {
  background-color: #f3fbff;
}
.compact-header {
  border-bottom-color: #ccc;
  border-bottom-style: solid;
  border-bottom-width: 1px;
  border-top-color: #999;
  border-top-style: solid;
  border-top-width: 1px !important;
}
.panel-group .panel + .panel {
  margin-top: 5px;
}
.panel-heading {
  padding: 10px 15px 10px 0;
  border-top-left-radius: 3px;
  border-top-right-radius: 3px;
}
</style>
