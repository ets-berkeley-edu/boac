<template>
  <div class="pt-3 pr-3 pl-3">
    <h1>Bulk Add Students</h1>
    <div>
      Create a curated group of students by adding their Student Identification (SID) numbers below.
    </div>
    <h2 class="page-section-header-sub mt-3">Add SID numbers</h2>
    <div>
      Type or paste a list of SID numbers. Example: 9999999990, 9999999991
    </div>
    <CuratedGroupBulkAdd :bulk-add-sids="bulkAddSids" />
    <b-modal
      id="modal"
      v-model="showCreateModal"
      body-class="pl-0 pr-0"
      hide-footer
      hide-header-close
      title="Name Your Curated Group"
      @shown="focusModalById('create-input')">
      <CreateCuratedGroupModal
        :sids="sids"
        :create="create"
        :cancel="cancel" />
    </b-modal>
  </div>
</template>

<script>
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal';
import CuratedGroupBulkAdd from '@/components/curated/CuratedGroupBulkAdd.vue';
import GoogleAnalytics from '@/mixins/GoogleAnalytics';
import Util from '@/mixins/Util';
import { createCuratedGroup } from '@/api/curated';

export default {
  name: 'CreateCuratedGroup',
  components: {CreateCuratedGroupModal, CuratedGroupBulkAdd},
  mixins: [GoogleAnalytics, Util],
  data: () => ({
    isCreatingCuratedGroup: false,
    showCreateModal: false,
    sids: undefined
  }),
  methods: {
    bulkAddSids(sids) {
      this.sids = sids;
      this.showCreateModal = true;
    },
    cancel() {
      this.showCreateModal = false;
    },
    create(name) {
      this.isCreatingCuratedGroup = true;
      this.showCreateModal = false;
      createCuratedGroup(name, this.sids)
        .then(group => {
          this.gaCuratedEvent(group.id, group.name, 'Create curated group with bulk SIDs');
          this.$router.push('/curate/' + group.id);
        });
    }
  }
}
</script>

<style scoped>

</style>
