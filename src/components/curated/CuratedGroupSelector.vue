<template>
  <div class="cohort-selector-container">
    <div>
      Selected sids: {{ sids }}
    </div>
    <div>
      <div class="cohort-selector-checkbox">
        <label id="checkbox-add-all-label"
               class="sr-only">Select all students to add to a curated group</label>
        <b-form-checkbox v-model="checked"
                         :indeterminate="indeterminate"
                         aria-describedby="students"
                         aria-controls="students"
                         @change="toggle">
          {{ checked ? 'Un-select All Students' : 'Select All Students' }}
         </b-form-checkbox>
      </div>
    </div>
    <div>
      <div class="cohort-btn-group"
           uib-dropdown
           is-open="selector.isOpen"
           v-if="showMenu">
        <button id="added-to-curated-cohort-confirmation"
                type="button"
                data-ng-disabled="true"
                class="btn cohort-btn-confirmation"
                v-if="isSaving">
          <i class="fas fa-check"></i>
          Added to Curated Group
        </button>
        <button id="add-to-curated-cohort-button"
                type="button"
                class="btn btn-primary"
                uib-dropdown-toggle
                v-if="!isSaving">
          Add to Curated Group <span class="caret"></span>
        </button>
        <ul class="dropdown-menu cohort-all-menu"
            uib-dropdown-menu
            role="menu"
            aria-labelledby="add-to-cohort-button">
          <li role="menuitem" v-if="isLoading">
            Loading <i class="fas fa-spinner fa-spin"></i>
          </li>
          <li role="menuitem" v-if="!curatedGroups.length">
            <span class="cohort-selector-zero-cohorts faint-text">You have no curated groups.</span>
          </li>
          <li role="menuitem"
              v-bind:class="{'cohort-checkbox-item': group, 'divider': !group}"
              v-for="(group, index) in curatedGroups"
              v-bind:key="group.id"
              data-ng-href="!isLoading">
            <input :id="'student-' + student.uid + '-curated-cohort-checkbox'"
                   type="checkbox"
                   v-model="group.selected"
                   v-on:click="curatedCohortCheckboxClick(group)"
                   :aria-labelledby="'curated-cohort-name-' + index"
                   v-if="group"/>
            <span :id="'curated-cohort-' + group.id + '-name'"
                  :aria-labelledby="'student-' + student.uid + '-cohort-checkbox'"
                  class="cohort-checkbox-name"
                  v-if="group">{{ group.name }}</span>
          </li>
          <li class="divider"></li>
          <!--
          <li role="menuitem"
              data-ng-controller="CreateCuratedCohortController"
              data-ng-href="!isLoading">
            <a id="curated-cohort-create"
               href
               v-on:click="openCreateCuratedCohortModal(onCreateCuratedCohort)"><i class="fas fa-plus"></i> Create New Curated Group</a>
          </li>
          -->
        </ul>
      </div>
    </div>
    <!--
    -->
  </div>
</template>

<script>
import _ from 'lodash';
import store from '@/store';

export default {
  name: 'CuratedGroupSelector',
  props: {
    students: Array
  },
  data: () => ({
    sids: [],
    checked: false,
    indeterminate: false,
    showMenu: false
  }),
  created() {
    this.$eventHub.$on('curated-group-checkbox-checked', sid => {
      this.sids.push(sid);
      this.refresh();
    });
    this.$eventHub.$on('curated-group-checkbox-unchecked', sid => {
      this.sids = _.remove(this.sids, s => s !== sid);
      this.refresh();
    });
  },
  computed: {
    curatedGroups() {
      return _.get(store.getters, 'user.myCuratedCohorts');
    }
  },
  methods: {
    toggle(checked) {
      this.sids = checked ? _.map(this.students, 'sid') : [];
      this.$eventHub.$emit(
        checked ? 'curated-group-select-all' : 'curated-group-deselect-all'
      );
    },
    refresh() {
      this.indeterminate = _.inRange(this.sids.length, 1, this.students.length);
      this.checked = this.sids.length === this.students.length;
    }
  }
};
</script>
