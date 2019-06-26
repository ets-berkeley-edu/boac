<template>
  <div
    :id="`home-curated-group-${curatedGroup.id}`"
    class="accordion panel"
    :class="{'panel-open': curatedGroup.isOpen}">
    <div class="panel-heading">
      <a
        :id="`home-curated-group-${curatedGroup.id}-toggle`"
        v-b-toggle="`home-curated-group-${curatedGroup.id}`"
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
              <span class="sr-only">{{ `${isOpen ? 'Hide' : 'Show'} details for curated group ` }}</span>
              <span>{{ curatedGroup.name }}</span>
              (<span>{{ curatedGroup.studentCount }}</span>
              <span class="sr-only">&nbsp;students</span>)
            </h2>
          </div>
          <div class="accordion-heading-count">
            <div class="sortable-table-header accordion-heading-count-label">
              Total Issues:
            </div>
            <div
              v-if="!curatedGroup.alertCount"
              class="home-issues-pill home-issues-pill-zero"
              aria-label="`No issues for ${cohort.name}`">0</div>
            <div
              v-if="curatedGroup.alertCount"
              class="home-issues-pill home-issues-pill-nonzero"
              aria-label="`${curatedGroup.alertCount} alerts for ${curatedGroup.name}`">{{ curatedGroup.alertCount }}</div>
          </div>
        </div>
      </a>
    </div>
    <b-collapse
      :id="`home-curated-group-${curatedGroup.id}`"
      :aria-expanded="isOpen"
      class="panel-body pr-3"
      :class="{'panel-open': isOpen}">
      <div v-if="curatedGroup.studentsWithAlerts && size(curatedGroup.studentsWithAlerts)">
        <div v-if="size(curatedGroup.studentsWithAlerts) === 50" :id="`home-curated-group-${curatedGroup.id}-alert-limited`" class="m-3">
          Showing 50 students with a high number of alerts.
          <router-link :id="`home-curated-group-${curatedGroup.id}-alert-limited-view-all`" :to="`/curated/${curatedGroup.id}`">
            View all {{ curatedGroup.studentCount }} students in "{{ curatedGroup.name }}"
          </router-link>
        </div>
        <SortableStudents :students="curatedGroup.studentsWithAlerts" :options="getSortOptions(curatedGroup)" />
      </div>
      <div>
        <router-link :id="`home-curated-group-${curatedGroup.id}-view-all`" :to="`/curated/${curatedGroup.id}`">
          <span v-if="curatedGroup.studentCount">
            View <span>{{ 'student' | pluralize(curatedGroup.studentCount,
                                                {1: 'the one', 'other': `all ${curatedGroup.studentCount}`}) }}
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
import Context from '@/mixins/Context';
import HomeUtil from '@/components/home/HomeUtil';
import SortableStudents from '@/components/search/SortableStudents';
import store from '@/store';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'HomeCuratedGroup',
  components: {
    SortableStudents
  },
  mixins: [Context, HomeUtil, UserMetadata, Util],
  props: {
    curatedGroup: Object
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
            this.alertScreenReader(`Loaded students with alerts who are in curated group ${this.curatedGroup.name}`);
            this.gaEvent(
              'Home',
              'Fetch students with alerts',
              `Curated Group: ${this.curatedGroup.name}`,
              this.curatedGroup.id
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
