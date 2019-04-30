<template>
  <div class="pt-3 pr-3 pl-3">
    <h1>Bulk Add Students</h1>
    <div v-if="curatedGroup">
      Add students to "<strong>{{ curatedGroup.name }}</strong>" by adding their Student Identification (SID) numbers below.
    </div>
    <div v-if="!curatedGroup">
      Create a curated group of students by adding their Student Identification (SID) numbers below.
    </div>
    <h2 class="page-section-header-sub mt-3">Add SID numbers</h2>
    <div>
      Type or paste a list of SID numbers. Example: 9999999990, 9999999991
    </div>
    <div class="mt-3 w-75">
      <div v-if="error || warning" class="alert-box p-3 mt-2 mb-3 w-100" :class="{'error': error, 'warning': warning}">
        <span aria-live="polite" role="alert" v-html="error || warning"></span>
      </div>
      <div>
        <b-form-textarea
          id="curated-group-bulk-add-sids"
          v-model="textarea"
          rows="8"
          max-rows="30"
          :disabled="isSaving"
        ></b-form-textarea>
      </div>
      <div class="d-flex justify-content-end mt-3">
        <b-btn
          id="btn-curated-group-bulk-add-sids"
          class="pl-2"
          variant="primary"
          :disabled="!trim(textarea) || isSaving"
          @click="submitSids">
          Next
        </b-btn>
      </div>
    </div>
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
        :create="createCuratedGroup"
        :cancel="cancelCuratedGroupModal" />
    </b-modal>
  </div>
</template>

<script>
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal';
import GoogleAnalytics from '@/mixins/GoogleAnalytics';
import Loading from '@/mixins/Loading';
import Util from '@/mixins/Util';
import { addStudents, createCuratedGroup, getCuratedGroup } from '@/api/curated';
import { validateSids } from '@/api/student';

export default {
  name: 'CuratedGroupBulkAdd',
  components: { CreateCuratedGroupModal },
  mixins: [GoogleAnalytics, Loading, Util],
  data: () => ({
    curatedGroup: undefined,
    error: undefined,
    isCreatingCuratedGroup: true,
    isSaving: false,
    showCreateModal: false,
    sids: undefined,
    textarea: undefined,
    warning: undefined
  }),
  mounted() {
    const id = this.toInt(this.get(this.$route, 'params.id'));
    if (id) {
      getCuratedGroup(id).then(data => {
        if (data) {
          this.curatedGroup = data;
          this.loaded();
        } else {
          this.$router.push({ path: '/404' });
        }
      });
    } else {
      this.loaded();
    }
  },
  methods: {
    cancelCuratedGroupModal() {
      this.showCreateModal = false;
      this.isSaving = false;
    },
    clearErrors() {
      this.error = null;
      this.warning = null;
    },
    createCuratedGroup(name) {
      this.isCreatingCuratedGroup = true;
      this.showCreateModal = false;
      createCuratedGroup(name, this.sids)
        .then(group => {
          this.gaCuratedEvent(group.id, group.name, 'Bulk add SIDs');
          this.$router.push('/curate/' + group.id);
          this.clearErrors();
        });
    },
    describeNotFound(sidList) {
      if (sidList.length === 1) {
        return `<strong>Uh oh!</strong> Student ${sidList[0]} not found. Please fix.`;
      } else {
        return `<strong>Uh oh!</strong> ${sidList.length} students not found: <ul class="mt-1 mb-0"><li>${this.join(sidList, '</li><li>')}</li></ul>`;
      }
    },
    submitSids() {
      this.sids = [];
      this.clearErrors();
      const trimmed = this.trim(this.textarea);
      if (trimmed) {
        const split = this.split(trimmed, ',');
        const notNumeric = this.partition(split, sid => /^\d+$/.test(this.trim(sid)))[1];
        if (notNumeric.length) {
          this.error = '<strong>Error!</strong> The list provided has not been properly formatted. Please fix.';
        } else {
          this.isSaving = true;
          validateSids(split).then(data => {
            const notFound = [];
            this.each(data, entry => {
              switch(entry.status) {
                case 200:
                case 401:
                  this.sids.push(entry.sid);
                  break;
                default:
                  notFound.push(entry.sid);
              }
            });
            if (notFound.length) {
              this.warning = this.describeNotFound(notFound);
              this.isSaving = false;
            } else if (this.curatedGroup) {
              const done = () => {
                this.gaCuratedEvent(
                  this.curatedGroup.id,
                  this.curatedGroup.name,
                  'Create new curated group via bulk-add students'
                );
                this.isSaving = false;
              };
              addStudents(this.curatedGroup, this.sids).finally(() => setTimeout(done, 2000));
              this.$router.push('/curate/' + this.curatedGroup.id);
            } else {
              this.showCreateModal = true;
            }
          });
        }
      } else {
        this.warning = 'Please provide one or more SIDs.';
      }
    }
  }
}
</script>

<style scoped>
.alert-box {
  border-radius: 5px;
  font-size: 18px;
  width: auto;
}
.error {
  background-color: #efd6d6;
  color: #9b393a;
}
.warning {
  background-color: #fbf7dc;
  color: #795f31;
}
</style>
