<template>
  <div class="cohort-selector-container">
    <div class="selector-checkbox-container">
      <label id="checkbox-add-all-label"
             class="sr-only">Select all students to add to a curated group</label>
      <b-form-checkbox plain
                       class="p-2 mr-0"
                       v-model="checked"
                       :indeterminate="indeterminate"
                       aria-describedby="students"
                       aria-controls="students"
                       @change="toggle">
        <span class="sr-only">{{ checked ? 'Un-select All Students' : 'Select All Students' }}</span>
       </b-form-checkbox>
    </div>
    <div>
      <b-dropdown class="ml-2"
                  variant="primary"
                  :disabled="isSaving"
                  v-if="showMenu">
        <template slot="button-content">
            <span v-if="!isSaving">Add to Curated Group</span>
          <!--
          <span :id="isSaving ? 'added-to-curated-cohort-confirmation' : 'add-to-curated-cohort-button'"
               class="d-flex align-items-center"
               :class="{'btn cohort-btn-confirmation': isSaving, 'btn btn-primary': !isSaving}">
            <span v-if="isSaving"><i class="fas fa-check"></i> Added to Curated Group</span>
          </span>
          -->
        </template>
        <b-dropdown-item v-if="reloading">
          Loading <i class="fas fa-spinner fa-spin"></i>
        </b-dropdown-item>
        <b-dropdown-item v-if="!curatedGroups.length">
          <span class="cohort-selector-zero-cohorts faint-text">You have no curated groups.</span>
        </b-dropdown-item>
        <b-dropdown-item class="cohort-checkbox-item"
                         v-for="(group, index) in curatedGroups"
                         :key="group.id"
                         v-if="group && !reloading">
          <input :id="'curated-group=' + group.id + '-checkbox'"
                 type="checkbox"
                 v-model="group.selected"
                 v-on:click="curatedGroupCheckboxClick(group)"
                 :aria-labelledby="'curated-cohort-name-' + index"
                 v-if="group"/>
          <span :id="'curated-cohort-' + group.id + '-name'"
                :aria-labelledby="'curated-group-' + group.id + '-checkbox'"
                class="cohort-checkbox-name"
                v-if="group">{{ group.name }}</span>
        </b-dropdown-item>
        <b-dropdown-divider v-if="!reloading"></b-dropdown-divider>
        <b-dropdown-item data-ng-controller="CreateCuratedGroupController"
                         v-if="!reloading">
          <span v-b-modal="'createCuratedGroupModal'"
                 class="btn-link cohort-manage-btn-link"
                 id="curated-cohort-create"
                 aria-label="Create a new curated group"
                 v-on:click="openCreateCuratedGroupModal(onCreateCuratedGroup)">
            <i class="fas fa-plus"></i> Create New Curated Group
          </span>
        </b-dropdown-item>
      </b-dropdown>
    </div>
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
    isSaving: false,
    reloading: false
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
      return _.get(store.getters.user, 'myCuratedCohorts') || [];
    },
    showMenu() {
      return this.sids.length;
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
    },
    curatedGroupCheckboxClick() {
      console.log('curatedGroupCheckboxClick!');
    },
    openCreateCuratedGroupModal() {
      console.log('openCreateCuratedGroupModal!');
    }
  }
};
</script>

<style scoped>
.selector-checkbox-container {
  background-color: #eee;
  border: 1px solid #aaa;
  border-radius: 4px;
  padding: 3px 0 3px 3px;
  text-align: center;
}
</style>
