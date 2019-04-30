<template>
  <div class="pt-3 pr-3 pl-3">
    <h1>Bulk Add Students</h1>
    <div v-if="curatedGroup">
      Add students to "<strong>{{ curatedGroup.name }}</strong>" by adding their Student Identification (SID) numbers below.
    </div>
    <div v-if="!curatedGroup">
      Create a curated group of students by adding their Student Identification (SID) numbers below.
    </div>
    <div class="mt-3 w-75">
      <div v-if="error" class="error p-3 mt-2 mb-3 w-100">
        <span aria-live="polite" role="alert"><strong>Uh oh!</strong> {{ error }}</span>
      </div>
      <div>
        <b-form-textarea
          id="curated-group-bulk-add-sids"
          v-model="sids"
          placeholder="Type or paste a list of SID numbers. Example: 3033223869, 3033112579"
          rows="8"
          max-rows="30"
          :disabled="isSaving"
          @change="clearError"
        ></b-form-textarea>
      </div>
      <div class="d-flex justify-content-end mt-3">
        <b-btn
          id="btn-curated-group-bulk-add-sids"
          class="pl-2"
          variant="primary"
          :disabled="isSaving"
          @click.stop="submitSids">
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
import Loading from '@/mixins/Loading';
import Util from '@/mixins/Util';
import { addStudents, createCuratedGroup, getCuratedGroup } from '@/api/curated';
import { validateSids } from '@/api/student';

export default {
  name: 'CuratedGroupBulkAdd',
  components: { CreateCuratedGroupModal },
  mixins: [Loading, Util],
  data: () => ({
    curatedGroup: undefined,
    error: undefined,
    isCreatingCuratedGroup: true,
    isSaving: false,
    showCreateModal: false,
    sids: undefined
  }),
  mounted() {
    const id = this.toInt(this.get(this.$route, 'params.id'));
    if (id) {
      getCuratedGroup(id).then(data => {
        if (data) {
          this.curatedGroup = data;
          this.setPageTitle(this.curatedGroup.name);
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
    clearError() {
      this.error = null;
    },
    submitSids() {
      const trimmed = this.trim(this.sids);
      if (trimmed) {
        const split = this.split(trimmed, ',');
        const notNumeric = this.partition(split, sid => this.toInt(sid))[1];
        if (notNumeric.length) {
          this.error = `Please fix the invalid entries: ${notNumeric}`;
        } else {
          validateSids(split).then(data => {
            const availableSids = [];
            const unavailable = [];
            const notFound = [];
            this.each(data, entry => {
              switch(entry.status) {
                case 200:
                  availableSids.push(entry.sid);
                  break;
                case 401:
                  unavailable.push(entry.sid);
                  break;
                default:
                  notFound.push(entry.sid);
              }
            });
            if (notFound || unavailable) {
              const badSids = notFound.concat(unavailable);
              const count = this.size(badSids);
              const pluralize = count === 1 ? '1 student' : `${count} students`;
              this.error = `${pluralize} not found: ${badSids.join(', ')}`;
            } else if (this.curatedGroup) {
              this.isSaving = true;
              const done = () => {
                this.gaCuratedEvent(
                  this.curatedGroup.id,
                  this.curatedGroup.name,
                  'Create new curated group via bulk-add students'
                );
                this.isSaving = false;
              };
              addStudents(this.curatedGroup, availableSids).finally(() => setTimeout(done, 2000));
              this.$router.push('/curate/' + this.curatedGroup.id);
            } else {
              this.showCreateModal = true;
            }
          });
        }
      } else {
        this.error = 'Please provide one or more SIDs.';
      }
    },
    createCuratedGroup(name) {
      this.isCreatingCuratedGroup = true;
      this.showCreateModal = false;
      createCuratedGroup(name, this.sids)
        .then(group => {
          this.each(
            [
              'create',
              `Added SIDs ${this.sid}, after create group`
            ],
            action => {
              this.gaCuratedEvent(group.id, group.name, action);
            }
          );
          this.$router.push('/curate/' + this.curatedGroup.id);
        });
    },
    cancelCuratedGroupModal() {
      this.showCreateModal = false;
    }
  }
}
</script>

<style scoped>
.error {
  background-color: #fbf7dc;
  border-radius: 5px;
  color: #795f31;
  font-size: 18px;
  width: auto;
}
</style>
