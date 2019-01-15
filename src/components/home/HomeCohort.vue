<template>
  <div :id="`home-cohort-${cohort.id}`"
       class="home-cohort-accordion panel"
       :class="{'panel-open': cohort.isOpen}">
    <div class="panel-heading">
      <a :id="`home-cohort-${cohort.id}-toggle`"
          v-b-toggle="`home-cohort-${cohort.id}`"
          class="home-cohort-accordion-heading-link"
          @click.prevent="fetchStudents()"
          tabindex="0"
          role="button"
          href="#">
        <div class="home-cohort-accordion-heading">
          <div class="home-cohort-accordion-heading-name">
            <div class="accordion-heading-caret">
              <i :id="`home-cohort-${cohort.id}-caret`"
                :aria-label="isFetching ? 'Loading cohort details' : ''"
                :class="{
                  'fas fa-spinner fa-spin': isFetching,
                  'fas fa-caret-right': !isOpen,
                  'fas fa-caret-down': isOpen
                }"></i>
            </div>
            <h2 class="page-section-header-sub accordion-header">
              <span class="sr-only">{{`${isOpen ? 'Hide' : 'Show'} details for cohort `}}</span>
              <span>{{ cohort.name }}</span>
              (<span :id="`home-cohort-${cohort.id}-total-student-count`">{{ cohort.totalStudentCount }}</span>
              <span class="sr-only">&nbsp;students</span>)
            </h2>
          </div>
          <div class="home-cohort-accordion-heading-count">
            <div class="group-summary-column-header home-cohort-accordion-heading-count-label">
              Total Issues:
            </div>
            <div class="home-issues-pill home-issues-pill-zero"
                  aria-label="`No issues for ${cohort.name}`"
                  v-if="!cohort.alertCount">0</div>
            <div class="home-issues-pill home-issues-pill-nonzero"
                  aria-label="`${cohort.alertCount} alerts for ${cohort.name}`"
                  v-if="cohort.alertCount">{{ cohort.alertCount }}</div>
          </div>
        </div>
      </a>
    </div>
    <b-collapse :id="`home-cohort-${cohort.id}`"
                :aria-expanded="isOpen"
                class="panel-body"
                :class="{'panel-open': isOpen}">
      <div v-if="cohort.studentsWithAlerts && size(cohort.studentsWithAlerts)">
        <SortableStudents :students="cohort.studentsWithAlerts"/>
      </div>
      <div>
        <router-link :id="`home-cohort-${cohort.id}-view-all`" :to="`/cohort/${cohort.id}`">
          <span v-if="cohort.totalStudentCount">
            View <span>{{'student' | pluralize(cohort.totalStudentCount,
                        {1: 'the one', 'other': `all ${cohort.totalStudentCount}`})}}
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
import SortableStudents from '@/components/search/SortableStudents.vue';
import store from '@/store';
import Util from '@/mixins/Util.vue';

export default {
  name: 'HomeCohort',
  components: {
    SortableStudents
  },
  mixins: [Util],
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
          });
      }
    }
  }
};
</script>

<style>
.panel-group {
  margin-bottom: 20px;
}
.panel-group .panel + .panel {
  margin-top: 5px;
}
.panel-heading {
  padding: 10px 15px;
  border-top-left-radius: 3px;
  border-top-right-radius: 3px;
}
</style>
