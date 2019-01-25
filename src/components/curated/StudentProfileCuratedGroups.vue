<template>
  <div>
    <div>
      <h3 class="student-bio-header">Curated Groups</h3>
    </div>
    <div v-if="myCuratedGroups && myCuratedGroups.length">
      <div class="student-curated-group-checkbox"
           v-for="(curatedGroup, curatedGroupIndex) in myCuratedGroups"
           :key="curatedGroupIndex">
        <input :id="`curated-group-checkbox-${curatedGroupIndex}`"
               type="checkbox"
               v-model="curatedGroupMemberships"
               :value="curatedGroup.id"
               @change="updateCuratedGroupMembership(curatedGroup)"
               :aria-label="(curatedGroupMemberships.includes(curatedGroup.id) ? 'Remove from' : 'Add to') + ' curated group ' + curatedGroup.name"/>
        <div>
          <router-link :to="`/curated_group/${curatedGroup.id}`">{{curatedGroup.name}}</router-link>
        </div>
      </div>
    </div>
    <div class="student-curated-group-checkbox"
         v-if="myCuratedGroups && !myCuratedGroups.length">
      <span class="faint-text">You have no curated groups.</span>
    </div>
    <div>
      <b-btn id="create-curated-group"
             variant="link"
             v-b-modal="'create-curated-group-modal'">
        <i class="fas fa-plus"></i> Create New Curated Group
      </b-btn>
    </div>
    <b-modal id="create-curated-group-modal"
             @shown="focusModalById('create-input')"
             body-class="pl-0 pr-0"
             v-model="showModal"
             hide-footer
             hide-header-close
             title="Name Your Curated Group">
      <CreateCuratedGroupModal :sids="[]"
                               :create="modalCreateCuratedGroup"
                               :cancel="modalCreateCuratedGroupCancel"/>
    </b-modal>
  </div>
</template>

<script>
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import {
  addStudents,
  createCuratedGroup,
  getMyCuratedGroupIdsPerStudentId,
  removeFromCuratedGroup
} from '@/api/curated';

export default {
  name: 'StudentProfileCuratedGroups',
  components: {
    CreateCuratedGroupModal
  },
  mixins: [UserMetadata, Util],
  props: {
    sid: String
  },
  data: () => ({
    curatedGroupMemberships: [],
    showModal: false
  }),
  created() {
    getMyCuratedGroupIdsPerStudentId(this.sid).then(data => {
      this.curatedGroupMemberships = data;
    });
  },
  methods: {
    modalCreateCuratedGroup(name) {
      this.showModal = false;
      createCuratedGroup(name, []);
    },
    modalCreateCuratedGroupCancel() {
      this.showModal = false;
    },
    updateCuratedGroupMembership(group) {
      if (this.includes(this.curatedGroupMemberships, group.id)) {
        addStudents(group, [this.student.sid]);
      } else {
        removeFromCuratedGroup(group.id, this.student.sid);
      }
    }
  }
};
</script>
