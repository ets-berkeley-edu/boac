<template>
  <div class="d-flex">
    <div
      class="selector-checkbox-container"
      :class="{'mr-1': showMenu, 'mr-3': !showMenu}">
      <label
        id="checkbox-add-all-label"
        class="sr-only">Select all students to add to a curated group</label>
      <b-form-checkbox
        id="add-all-to-curated-group"
        v-model="isSelectAllChecked"
        class="add-all-checkbox mr-0"
        plain
        :disabled="isSaving"
        :indeterminate="indeterminate"
        aria-describedby="checkbox-add-all-label"
        aria-controls="curated-group-dropdown-select"
        @change="toggle">
        <span class="sr-only">{{ isSelectAllChecked ? 'Un-select All Students' : 'Select All Students' }}</span>
      </b-form-checkbox>
    </div>
    <div>
      <b-dropdown
        v-if="showMenu"
        id="curated-group-dropdown-select"
        class="curated-selector mr-3"
        :variant="dropdownVariant"
        toggle-class="b-dd-override"
        size="sm"
        no-caret
        :disabled="disableSelector">
        <template slot="button-content">
          <span
            :id="isSaving ? 'add-to-curated-group-confirmation' : 'add-to-curated-group'"
            class="p-3">
            <span v-if="!isSaving">
              <span class="pr-2">Add to Curated Group</span>
              <i v-if="disableSelector" class="fas fa-spinner fa-spin"></i>
              <i v-if="!disableSelector" class="fas fa-caret-down"></i>
            </span>
            <span v-if="isSaving">
              <i class="fas fa-check"></i> Added to Curated Group
              <span
                role="alert"
                aria-live="passive"
                class="sr-only">Selected students added to the chosen curated group</span>
            </span>
          </span>
        </template>
        <b-dropdown-item v-if="!size(myCuratedGroups)">
          <span class="cohort-selector-zero-cohorts faint-text">You have no curated groups.</span>
        </b-dropdown-item>
        <b-dropdown-item
          v-for="group in myCuratedGroups"
          :id="`curated-group-${group.id}-menu-item`"
          :key="group.id"
          class="b-dd-item-override"
          @keyup.space.prevent.stop="curatedGroupCheckboxClick(group)">
          <input
            v-if="group"
            :id="`curated-group-${group.id}-checkbox`"
            type="checkbox"
            :aria-labelledby="`curated-group-${group.id}-name`"
            @click="curatedGroupCheckboxClick(group)" />
          <label
            v-if="group"
            :id="`curated-group-${group.id}-name`"
            class="cohort-checkbox-name pb-0 pt-0"
            :aria-label="`Add students to curated group '${group.name}'`">{{ group.name }}</label>
        </b-dropdown-item>
        <b-dropdown-divider></b-dropdown-divider>
        <b-dropdown-item>
          <b-btn
            id="create-curated-group"
            v-b-modal="'modal'"
            class="text-dark"
            variant="link"
            aria-label="Create a new curated group">
            <i class="fas fa-plus"></i> Create New Curated Group
          </b-btn>
        </b-dropdown-item>
      </b-dropdown>
      <b-modal
        id="modal"
        v-model="showModal"
        body-class="pl-0 pr-0"
        hide-footer
        hide-header-close
        title="Name Your Curated Group"
        @shown="focusModalById('create-input')">
        <CreateCuratedGroupModal
          :sids="sids"
          :create="modalCreateCuratedGroup"
          :cancel="modalCancel" />
      </b-modal>
    </div>
  </div>
</template>

<script>
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal';
import GoogleAnalytics from '@/mixins/GoogleAnalytics';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { addStudents, createCuratedGroup } from '@/api/curated';

export default {
  name: 'CuratedGroupSelector',
  components: {
    CreateCuratedGroupModal
  },
  mixins: [GoogleAnalytics, UserMetadata, Util],
  props: {
    contextDescription: String,
    students: Array
  },
  data: () => ({
    sids: [],
    isSelectAllChecked: false,
    indeterminate: false,
    isSaving: false,
    showModal: false
  }),
  computed: {
    disableSelector() {
      return this.isSaving || this.isNil(this.myCuratedGroups);
    },
    dropdownVariant() {
      return this.isSaving ? 'success' : 'primary';
    },
    showMenu() {
      return this.size(this.sids);
    }
  },
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
  methods: {
    toggle(checked) {
      if (checked) {
        this.sids = this.map(this.students, 'sid');
        this.$eventHub.$emit('curated-group-select-all');
        this.putFocusNextTick('curated-group-dropdown-select', 'button');
      } else {
        this.sids = [];
        this.$eventHub.$emit('curated-group-deselect-all');
      }
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
        this.$eventHub.$emit('curated-group-deselect-all');
        this.isSaving = false;
        this.gaCuratedEvent(
          group.id,
          group.name,
          `${this.contextDescription}: add students`
        );
      };
      const done = () => (self.isSaving = false);
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
      const trackEvent = group => {
        this.each(
          [
            'create',
            `${this.contextDescription}: add students, after create group`
          ],
          action => {
            this.gaCuratedEvent(group.id, group.name, action);
          }
        );
      };
      createCuratedGroup(name, this.sids)
        .then(trackEvent)
        .finally(() => setTimeout(() => done(), 2000));
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
