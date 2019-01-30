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
.accordion-header {
  margin: 0;
}
.accordion-heading-caret {
  color: #337ab7;
  margin-right: 15px;
  width: 10px;
}
.home-cohort-accordion-heading {
  background: #ecf5fb;
  display: flex;
  justify-content: space-between;
}
.home-cohort-accordion-heading-count {
  align-items: center;
  display: flex;
  margin: 10px 15px;
  min-width: 130px;
}
.home-cohort-accordion-heading-count-label {
  margin: 0 5px;
}
.home-cohort-accordion-heading-name {
  align-items: center;
  display: flex;
  margin: 10px 15px;
}
.home-cohort-accordion .panel-title a:focus,
.home-cohort-accordion .panel-title a:hover {
  text-decoration: none;
}
.home-inactive-info-icon {
  color: #d0021b;
  font-size: 16px;
}
.home-issues-pill {
  border-radius: 10px;
  color: #fff;
  font-size: 16px;
  font-weight: 800;
  height: 20px;
  line-height: 20px;
  margin: 0 auto;
  text-align: center;
  width: 30px;
}
.home-issues-pill-nonzero {
  background-color: #f0ad4e;
}
.home-issues-pill-zero {
  background-color: #ccc;
}
</style>

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
