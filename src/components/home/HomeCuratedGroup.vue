<template>
  <div :id="`home-curated-cohort-${index}`"
       class="home-cohort-accordion panel"
       :class="{'panel-open': curatedGroup.isOpen}">
    <div class="panel-heading">
      <a :id="`home-curated-cohort-${index}-toggle`"
          v-b-toggle="`home-curated-cohort-${index}`"
          class="home-cohort-accordion-heading-link"
          @click.prevent="fetchStudents()"
          tabindex="0"
          role="button"
          href="#">
        <div class="home-cohort-accordion-heading">
          <div class="home-cohort-accordion-heading-name">
            <div class="accordion-heading-caret">
              <i :id="`home-curated-cohort-${index}-caret`"
                :aria-label="isOpen ? 'Hide curated group details' : 'Show curated group details'"
                :class="{
                  'fas fa-spinner fa-spin': isFetching,
                  'fas fa-caret-right': !isOpen,
                  'fas fa-caret-down': isOpen
                }"></i>
            </div>
            <h2 class="page-section-header-sub accordion-header">
              <span>{{ curatedGroup.name }}</span>
              (<span>{{ curatedGroup.studentCount }}</span>)
            </h2>
          </div>
          <div class="home-cohort-accordion-heading-count">
            <div class="group-summary-column-header home-cohort-accordion-heading-count-label">
              Total Issues:
            </div>
            <div class="home-issues-pill home-issues-pill-zero"
                  aria-label="`No issues for ${cohort.name}`"
                  v-if="!curatedGroup.alertCount">0</div>
            <div class="home-issues-pill home-issues-pill-nonzero"
                  aria-label="`${curatedGroup.alertCount} alerts for ${curatedGroup.name}`"
                  v-if="curatedGroup.alertCount">{{ curatedGroup.alertCount }}</div>
          </div>
        </div>
      </a>
    </div>
    <b-collapse :id="`home-curated-cohort-${index}`"
                :aria-expanded="isOpen"
                class="panel-body"
                :class="{'panel-open': isOpen}">
      <div v-if="curatedGroup.studentsWithAlerts && size(curatedGroup.studentsWithAlerts)">
        <SortableStudents :students="curatedGroup.studentsWithAlerts"/>
      </div>
      <div>
        <router-link :id="`home-curated-cohort-${index}-view-all`" :to="`/curated_group/${curatedGroup.id}`">
          <span v-if="curatedGroup.studentCount">
            View <span>{{'student' | pluralize(curatedGroup.studentCount,
                        {1: 'the one', 'other': `all ${curatedGroup.studentCount}`})}}
                  </span>
            in "<span>{{ curatedGroup.name }}</span>"
          </span>
          <span v-if="!curatedGroup.studentCount">
            "<span>{{ curatedGroup.name }}</span>" has 0 students
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
  name: 'HomeCuratedGroup',
  components: {
    SortableStudents
  },
  mixins: [Util],
  props: {
    curatedGroup: Object,
    index: Number
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
          .dispatch('curated/loadStudentsWithAlerts', this.curatedGroup.id)
          .then(curatedGroup => {
            this.curatedGroup = curatedGroup;
            this.isFetching = false;
          });
      }
    }
  }
};
</script>

<style src="./home.css">
</style>
