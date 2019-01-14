<template>
  <div class="d-flex">
    <div class="selector-checkbox-container"
         :class="{'mr-1': showMenu, 'mr-3': !showMenu}">
      <label id="checkbox-add-all-label"
             class="sr-only">Select all students to add to a curated group</label>
      <b-form-checkbox id="curated-cohort-checkbox-add-all"
                       class="add-all-checkbox"
                       plain
                       :disabled="isSaving"
                       v-model="isSelectAllChecked"
                       :indeterminate="indeterminate"
                       aria-describedby="checkbox-add-all-label"
                       aria-controls="curated-group-dropdown-select"
                       @change="toggle">
        <span class="sr-only">{{ isSelectAllChecked ? 'Un-select All Students' : 'Select All Students' }}</span>
      </b-form-checkbox>
    </div>
    <div>
      <b-dropdown id="curated-group-dropdown-select"
                  class="curated-selector mr-3"
                  :variant="dropdownVariant"
                  toggle-class="b-dd-primary-override"
                  size="sm"
                  no-caret
                  :disabled="isSaving"
                  v-if="showMenu">
        <template slot="button-content">
          <span :id="isSaving ? 'added-to-curated-cohort-confirmation' : 'add-to-curated-cohort-button'"
                class="p-3">
            <span v-if="!isSaving">Add to Curated Group <i class="fas fa-caret-down"></i></span>
            <span v-if="isSaving">
              <i class="fas fa-check"></i> Added to Curated Group
              <span role="alert"
                    aria-live="passive"
                    class="sr-only">Selected students added to the chosen curated group</span>
            </span>
          </span>
        </template>
        <b-dropdown-item v-if="!size(curatedGroups)">
          <span class="cohort-selector-zero-cohorts faint-text">You have no curated groups.</span>
        </b-dropdown-item>
        <b-dropdown-item :id="`curated-group-${group.id}-menu-item`"
                         class="b-dd-item-override"
                         v-for="group in curatedGroups"
                         :key="group.id"
                         v-if="group && !reloading">
          <input :id="`curated-group-${group.id}-checkbox`"
                 type="checkbox"
                 v-model="group.selected"
                 @click="curatedGroupCheckboxClick(group)"
                 :aria-labelledby="`curated-cohort-${group.id}-name`"
                 v-if="group"/>
          <label :id="`curated-cohort-${group.id}-name`"
                 class="cohort-checkbox-name pb-0 pt-0"
                 :aria-label="`Add students to curated group '${group.name}'`"
                 v-if="group">{{ group.name }}</label>
        </b-dropdown-item>
        <b-dropdown-divider></b-dropdown-divider>
        <b-dropdown-item id="curated-cohort-create-menu-item">
          <b-btn id="curated-cohort-create"
                 class="text-dark"
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
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal.vue';
import store from '@/store';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { addStudents, createCuratedGroup } from '@/api/curated';

export default {
  name: 'CuratedGroupSelector',
  mixins: [UserMetadata, Util],
  components: {
    CreateCuratedGroupModal
  },
  props: {
    students: Array
  },
  data: () => ({
    sids: [],
    curatedGroups: store.getters['curated/myCuratedGroups'],
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
      this.sids = this.remove(this.sids, s => s !== sid);
      this.refresh();
    });
  },
  computed: {
    dropdownVariant() {
      return this.isSaving ? 'success' : 'primary';
    },
    showMenu() {
      return this.size(this.sids);
    }
  },
  methods: {
    toggle(checked) {
      this.sids = checked ? this.map(this.students, 'sid') : [];
      let event = checked
        ? 'curated-group-select-all'
        : 'curated-group-deselect-all';
      this.$eventHub.$emit(event);
    },
    refresh() {
      this.indeterminate = this.inRange(
        this.size(this.sids),
        1,
        this.size(this.students)
      );
      this.isSelectAllChecked =
        this.size(this.sids) === this.size(this.students);
    },
    curatedGroupCheckboxClick(group) {
      const afterAddStudents = () => {
        this.sids = [];
        this.isSelectAllChecked = this.indeterminate = false;
        this.each(this.curatedGroups, g => (g.selected = false));
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
.add-all-checkbox {
  padding: 5px 0 0 1px;
}
label {
  font-size: 14px;
  margin-bottom: 0;
}
.selector-checkbox-container {
  background-color: #eee;
  border: 1px solid #aaa;
  border-radius: 4px;
  height: 34px;
  width: 34px;
  padding: 3px 0 3px 3px;
  text-align: center;
}
.curated-selector {
  height: 35px;
}
</style>
