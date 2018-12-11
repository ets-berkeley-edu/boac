<template>
  <div class="cohort-selector-container">
    <div class="selector-checkbox-container">
      <label id="checkbox-add-all-label"
             class="sr-only">Select all students to add to a curated group</label>
      <b-form-checkbox plain
                       class="p-2 mr-0"
                       :disabled="isSaving"
                       v-model="isSelectAllChecked"
                       :indeterminate="indeterminate"
                       aria-describedby="students"
                       aria-controls="students"
                       @change="toggle">
        <span class="sr-only">{{ isSelectAllChecked ? 'Un-select All Students' : 'Select All Students' }}</span>
      </b-form-checkbox>
    </div>
    <div>
      <b-dropdown class="ml-2"
                  no-caret
                  :variant="isSaving ? 'success' : 'primary'"
                  :disabled="isSaving"
                  v-if="showMenu">
        <template slot="button-content">
          <span :id="isSaving ? 'added-to-curated-cohort-confirmation' : 'add-to-curated-cohort-button'"
                class="p-0 pr-1">
            <span v-if="!isSaving">Add to Curated Group <i class="fas fa-caret-down pl-1"></i></span>
            <span v-if="isSaving"><i class="fas fa-check"></i> Added to Curated Group</span>
          </span>
        </template>
        <b-dropdown-item v-if="!curatedGroups.length">
          <span class="cohort-selector-zero-cohorts faint-text">You have no curated groups.</span>
        </b-dropdown-item>
        <b-dropdown-item :id="'curated-group-' + group.id + '-menu-item'"
                         href
                         class="cohort-checkbox-item"
                         v-for="(group, index) in curatedGroups"
                         :key="group.id"
                         v-if="group && !reloading">
          <input :id="'curated-group-' + group.id + '-checkbox'"
                 type="checkbox"
                 v-model="group.selected"
                 @click="curatedGroupCheckboxClick(group)"
                 :aria-labelledby="'curated-cohort-name-' + index"
                 v-if="group"/>
          <span :id="'curated-cohort-' + group.id + '-name'"
                :aria-labelledby="'curated-group-' + group.id + '-checkbox'"
                class="cohort-checkbox-name"
                v-if="group">{{ group.name }}</span>
        </b-dropdown-item>
        <b-dropdown-divider></b-dropdown-divider>
        <b-dropdown-item id="curated-cohort-create-menu-item">
          <b-btn id="curated-cohort-create"
                 variant="link"
                 v-b-modal="'modal'"
                 aria-label="Create a new curated group">
            <i class="fas fa-plus"></i> Create New Curated Group
          </b-btn>
        </b-dropdown-item>
      </b-dropdown>
      <b-modal id="modal"
               v-model="showModal"
               hide-footer
               hide-header-close
               title="Name Your Curated Group">
        <CreateCuratedGroupModal :sids="sids"
                                 :create="modalCreateCuratedGroup"
                                 :cancel="modalCancel"/>
      </b-modal>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal.vue';
import UserMetadata from '@/mixins/UserMetadata';
import { addStudents, createCuratedGroup } from '@/api/curated';

export default {
  name: 'CuratedGroupSelector',
  mixins: [UserMetadata],
  components: {
    CreateCuratedGroupModal
  },
  props: {
    students: Array
  },
  data: () => ({
    sids: [],
    isSelectAllChecked: false,
    indeterminate: false,
    isSaving: false,
    reloading: false,
    showModal: false
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
      return _.get(this.user, 'myCuratedCohorts') || [];
    },
    showMenu() {
      return this.sids.length;
    }
  },
  methods: {
    toggle(checked) {
      this.sids = checked ? _.map(this.students, 'sid') : [];
      let event = checked
        ? 'curated-group-select-all'
        : 'curated-group-deselect-all';
      this.$eventHub.$emit(event);
    },
    refresh() {
      this.indeterminate = _.inRange(this.sids.length, 1, this.students.length);
      this.isSelectAllChecked = this.sids.length === this.students.length;
    },
    curatedGroupCheckboxClick(group) {
      const afterAddStudents = () => {
        this.sids = [];
        this.isSelectAllChecked = this.indeterminate = false;
        _.each(this.curatedGroups, g => (g.selected = false));
        this.$eventHub.$emit('curated-group-deselect-all');
        this.isSaving = false;
      };
      const done = () => (group.selected = self.isSaving = false);
      this.isSaving = true;
      addStudents(group, this.sids)
        .then(afterAddStudents)
        .finally(() => setTimeout(done, 1000));
    },
    modalCreateCuratedGroup(name) {
      this.isSaving = true;
      this.showModal = false;
      let done = () => {
        this.sids = [];
        this.refresh();
        this.toggle(false);
        this.isSaving = false;
      };
      createCuratedGroup(name, this.sids).then(done);
    },
    modalCancel() {
      this.sids = [];
      this.refresh();
      this.toggle(false);
      this.showModal = false;
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
