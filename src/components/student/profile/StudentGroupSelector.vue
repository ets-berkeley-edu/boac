<template>
  <div>
    <b-dropdown
      id="curated-group-dropdown"
      :variant="dropdownVariant"
      toggle-class="b-dd-override b-dd-narrow"
      menu-class="groups-menu-class"
      size="sm"
      no-caret
      :disabled="disableSelector">
      <template slot="button-content">
        <span
          :id="isAdding ? 'added-to-curated-group' : (isRemoving ? 'removed-from-curated-group' : 'add-to-curated-group')"
          class="p-3">
          <span v-if="!isAdding && !isRemoving">
            <span class="pr-1">Add to Group</span>
            <font-awesome
              v-if="disableSelector || groupsLoading"
              icon="spinner"
              spin
              class="caret-down-width" />
            <font-awesome v-if="!disableSelector && !groupsLoading" icon="caret-down" class="caret-down-width" />
          </span>
          <span v-if="isRemoving">
            <font-awesome icon="times" /> Removed
            <span
              role="alert"
              aria-live="passive"
              class="sr-only">Student removed from the selected group</span>
          </span>
          <span v-if="isAdding">
            <font-awesome icon="check" /> Added
            <span
              role="alert"
              aria-live="passive"
              class="sr-only">Student added to the selected group</span>
          </span>
        </span>
      </template>
      <b-dropdown-item v-if="!size(myCuratedGroups)">
        <span class="text-nowrap pb-1 pl-3 pr-3 pt-1 faint-text">You have no curated groups.</span>
      </b-dropdown-item>
      <div v-if="!groupsLoading" class="pt-1">
        <b-dropdown-item
          v-for="group in myCuratedGroups"
          :id="`curated-group-${group.id}-menu-item`"
          :key="group.id"
          class="b-dd-item-override"
          @keyup.space.prevent.stop="groupCheckboxClick(group)">
          <input
            :id="`curated-group-${group.id}-checkbox`"
            v-model="checkedGroups"
            type="checkbox"
            :value="group.id"
            :aria-label="`${checkedGroups.includes(group.id) ? 'Checked' : 'Not checked'}`"
            @click="groupCheckboxClick(group)" />
          <label
            :id="`curated-group-${group.id}-name`"
            :for="`curated-group-${group.id}-checkbox`"
            class="curated-checkbox-label pb-0 pt-0"
            :aria-label="`${checkedGroups.includes(group.id) ? 'Remove student from' : 'Add student to'} group '${group.name}'`">{{ group.name }}</label>
        </b-dropdown-item>
      </div>
      <b-dropdown-divider></b-dropdown-divider>
      <b-dropdown-item>
        <b-btn
          id="create-curated-group"
          v-b-modal="'modal'"
          class="create-new-button mb-0 pl-0 text-dark"
          variant="link"
          aria-label="Create a new curated group">
          <font-awesome icon="plus" /> Create New Curated Group
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
        :sids="[ sid ]"
        :create="modalCreateGroup"
        :cancel="modalCancel" />
    </b-modal>
  </div>
</template>

<script>
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal';
import GoogleAnalytics from '@/mixins/GoogleAnalytics';
import Scrollable from '@/mixins/Scrollable';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import {
  addStudents,
  createCuratedGroup,
  getMyCuratedGroupIdsPerStudentId,
  removeFromCuratedGroup
} from '@/api/curated';

export default {
  name: 'StudentGroupSelector',
  components: {
    CreateCuratedGroupModal
  },
  mixins: [GoogleAnalytics, Scrollable, UserMetadata, Util],
  props: {
    sid: {
      type: String,
      required: true
    }
  },
  data: () => ({
    checkedGroups: undefined,
    groupsLoading: true,
    isAdding: false,
    isRemoving: false,
    showModal: false
  }),
  computed: {
    disableSelector() {
      return this.isAdding || this.isRemoving;
    },
    dropdownVariant() {
      return this.isAdding
        ? 'success'
        : this.isRemoving
          ? 'warning'
          : 'primary';
    }
  },
  created() {
    getMyCuratedGroupIdsPerStudentId(this.sid).then(data => {
      this.checkedGroups = data;
      this.groupsLoading = false;
    });
  },
  methods: {
    groupCheckboxClick(group) {
      if (this.includes(this.checkedGroups, group.id)) {
        this.isRemoving = true;
        const done = () => {
          this.checkedGroups = this.without(this.checkedGroups, group.id);
          this.isRemoving = false;
          this.putFocusNextTick('curated-group-dropdown', 'button');
          this.gaCuratedEvent(
            group.id,
            group.name,
            `Student profile: Removed SID ${this.sid}`
          );
        };
        removeFromCuratedGroup(group.id, this.sid).finally(() =>
          setTimeout(done, 2000)
        );
      } else {
        this.isAdding = true;
        const done = () => {
          this.checkedGroups.push(group.id);
          this.isAdding = false;
          this.putFocusNextTick('curated-group-dropdown', 'button');
          this.gaCuratedEvent(
            group.id,
            group.name,
            `Student profile: Added SID ${this.sid}`
          );
        };
        addStudents(group, [this.sid]).finally(() => setTimeout(done, 2000));
      }
    },
    modalCreateGroup(name) {
      this.isAdding = true;
      this.showModal = false;
      createCuratedGroup(name, [this.sid])
        .then(group => {
          this.checkedGroups.push(group.id);
          this.each(
            [
              'create',
              `Student profile: Added SID ${this.sid}, after create group`
            ],
            action => {
              this.gaCuratedEvent(group.id, group.name, action);
            }
          );
          setTimeout(() => this.isAdding = false, 2000)
        });
    },
    modalCancel() {
      this.showModal = false;
    }
  }
};
</script>

<style scoped>
.caret-down-width {
  width: 15px;
}
.create-new-button {
  font-size: 16px;
}
.groups-menu-class {
  height: 35px !important;
  min-width: 160px !important;
  width: 160px !important;
}
</style>
