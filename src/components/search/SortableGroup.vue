<template>
  <div
    :id="`sortable-${keyword}-${group.id}`"
    class="accordion panel"
    :class="{'panel-open pb-3': openAndLoaded}">
    <div
      class="panel-heading"
      :class="{'compact-background': compact && isOpen, 'bg-white': compact && !isOpen, 'p-0': compact}">
      <a
        :id="`sortable-${keyword}-${group.id}-toggle`"
        v-b-toggle="`sortable-${keyword}-${group.id}`"
        class="accordion-heading-link"
        tabindex="0"
        role="button"
        href="#"
        @click.prevent="fetchStudents()">
        <div
          class="accordion-heading d-flex justify-content-between"
          :class="{'compact-header compact-border-bottom': compact && openAndLoaded, 'bg-white': isFetching || !isOpen}">
          <div class="accordion-heading-name align-items-start d-flex">
            <div class="accordion-heading-caret">
              <font-awesome v-if="isFetching" icon="spinner" spin />
              <font-awesome v-if="!isFetching" :icon="isOpen ? 'caret-down' : 'caret-right'" />
            </div>
            <h2 class="page-section-header-sub m-0 text-wrap">
              <span class="sr-only">{{ `${isOpen ? 'Hide' : 'Show'} details for ${keyword} ` }}</span>
              <span>{{ group.name }}</span>
              (<span :id="`sortable-${keyword}-${group.id}-total-student-count`">{{ group.totalStudentCount }}</span>
              <span class="sr-only">&nbsp;students</span>)
            </h2>
          </div>
          <div class="accordion-heading-count align-items-start d-flex justify-content-end">
            <div v-if="!compact" class="sortable-table-header accordion-heading-count-label">
              Total Issues:
            </div>
            <div
              v-if="!group.alertCount"
              class="pill-alerts pill-alerts-zero"
              aria-label="`No issues for ${group.name}`">0</div>
            <div
              v-if="group.alertCount"
              class="font-weight-normal pill-alerts pill-alerts-nonzero pl-2 pr-2"
              aria-label="`${group.alertCount} alerts for ${group.name}`">{{ group.alertCount }}</div>
          </div>
        </div>
      </a>
    </div>
    <b-collapse
      :id="`sortable-${keyword}-${group.id}`"
      :aria-expanded="openAndLoaded"
      class="panel-body pr-3"
      :class="{'panel-open': openAndLoaded, 'compact-background': compact && !isFetching, 'compact-border-bottom': compact && openAndLoaded}">
      <div v-if="studentsWithAlerts && size(studentsWithAlerts)">
        <div v-if="!compact && size(studentsWithAlerts) === 50" :id="`sortable-${keyword}-${group.id}-alert-limited`" class="m-3">
          Showing 50 students with a high number of alerts.
          <router-link :id="`sortable-${keyword}-${group.id}-alert-limited-view-all`" :to="`/${keyword}/${group.id}`">
            View all {{ group.totalStudentCount }} students in "{{ group.name }}"
          </router-link>
        </div>
        <div class="pt-2">
          <SortableStudents
            :students="studentsWithAlerts"
            :options="sortableStudentsOptions(group, compact)" />
        </div>
      </div>
      <div v-if="openAndLoaded" class="mb-3 ml-4">
        <router-link :id="`sortable-${keyword}-${group.id}-view-all`" :to="`/${keyword}/${group.id}`">
          <span v-if="group.totalStudentCount">
            View <span>{{ 'student' | pluralize(group.totalStudentCount, {1: 'the one', 'other': `all ${group.totalStudentCount}`}) }}</span>
            in "<span>{{ group.name }}</span>"
          </span>
          <div v-if="!group.totalStudentCount" class="pt-3">
            "<span>{{ group.name }}</span>" has 0 students
          </div>
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
  name: 'SortableGroup',
  components: {SortableStudents},
  mixins: [Berkeley, Context, UserMetadata, Util],
  props: {
    compact: {
      default: false,
      type: Boolean
    },
    group: {
      required: true,
      type: Object
    },
    isCohort: {
      required: true,
      type: Boolean
    }
  },
  data: () => ({
    isFetching: undefined,
    isOpen: undefined,
    keyword: undefined,
    studentsWithAlerts: undefined
  }),
  computed: {
    openAndLoaded() {
      return this.isOpen && !this.isFetching;
    }
  },
  mounted() {
    this.keyword = this.isCohort ? 'cohort' : 'curated';
  },
  methods: {
    fetchStudents() {
      this.isOpen = !this.isOpen;
      if (this.isNil(this.studentsWithAlerts)) {
        this.isFetching = true;
        const ga = this.isCohort ? this.gaCohortEvent : this.gaCuratedEvent;
        store
          .dispatch(`${this.keyword}/loadStudentsWithAlerts`, this.group.id)
          .then(group => {
            this.studentsWithAlerts = group.studentsWithAlerts;
            this.isFetching = false;
            this.alertScreenReader(`Loaded students with alerts who are in ${this.keyword} ${this.group.name}`);
            ga({
              id: this.group.id,
              name: this.group.name,
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
.compact-border-bottom {
  border-bottom-color: #ccc;
  border-bottom-style: solid;
  border-bottom-width: 1px;
}
.compact-header {
  border-top-color: #999;
  border-top-style: solid;
  border-top-width: 1px;
}
.panel-heading {
  padding: 10px 15px 10px 0;
  border-top-left-radius: 3px;
  border-top-right-radius: 3px;
}
</style>

<style>
.accordion .panel-title a:focus,
.accordion .panel-title a:hover {
  text-decoration: none;
}
.accordion-heading {
  background: #ecf5fb;
}
.accordion-heading-caret {
  color: #337ab7;
  margin-right: 15px;
  width: 10px;
}
.accordion-heading-count {
  margin: 10px 15px;
  min-width: 130px;
}
.accordion-heading-count-label {
  margin: 0 5px;
}
.accordion-heading-name {
  margin: 10px 15px;
}
.accordion-heading-link:active,
.accordion-heading-link:focus,
.accordion-heading-link:hover {
  text-decoration: none;
}
</style>
