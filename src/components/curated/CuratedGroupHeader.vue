<template>
  <div class="d-flex justify-content-between mb-2">
    <div v-if="!renameMode.on">
      <h1 tabindex="0" ref="pageHeader" class="page-section-header mt-0">
        <span>{{ curatedGroup.name || 'Curated Group' }}</span>
        <span class="faint-text"> (<span>{{ 'student' | pluralize(curatedGroup.studentCount, {1: 'One'})}}</span>)</span>
      </h1>
    </div>
    <div class="w-100 mr-3" v-if="renameMode.on">
      <div>
        <form @submit="rename">
          <input id="rename-input"
                 class="form-control"
                 aria-label="Curated group name, 255 characters or fewer"
                 aria-required="true"
                 :aria-invalid="!renameMode.input"
                 @input="renameMode.hideError = true"
                 v-model="renameMode.input"
                 ref="input"
                 maxlength="255"
                 name="name"
                 required
                 type="text"/>
        </form>
      </div>
      <div class="has-error mb-2"
           v-if="renameMode.error && !renameMode.hideError">
        {{ renameMode.error }}
      </div>
      <div class="faint-text mb-3">255 character limit <span v-if="renameMode.input.length">({{255 - renameMode.input.length}} left)</span></div>
    </div>
    <div class="d-flex align-self-baseline mr-4" v-if="renameMode.on">
      <b-btn id="rename-confirm"
             class="btn-primary-color-override"
             variant="primary"
             size="sm"
             aria-label="Save changes to curated group name"
             @click.stop="rename"
             :disabled="!renameMode.input">
        Rename
      </b-btn>
      <b-btn id="rename-cancel"
             class="cohort-manage-btn"
             variant="link"
             aria-label="Cancel rename curated group"
             size="sm"
             @click="exitRenameMode">
        Cancel
      </b-btn>
    </div>
    <div class="d-flex align-items-center mr-4" v-if="!renameMode.on">
      <div>
        <b-btn id="rename-button"
               variant="link"
               aria-label="Rename this curated group"
               @click="enterRenameMode">
          Rename
        </b-btn>
      </div>
      <div class="faint-text">|</div>
      <div>
        <b-btn id="delete-button"
               variant="link"
               aria-label="Delete this curated group"
               v-b-modal="'myModal'">
          Delete
        </b-btn>
        <b-modal id="myModal"
                 v-model="isModalOpen">
          <div slot="modal-header">
            <h3>Delete Curated Group</h3>
          </div>
          <div class="modal-body curated-cohort-label" id="confirm-delete-body">
            Are you sure you want to delete "<strong>{{ curatedGroup.name }}</strong>"?
          </div>
          <div slot="modal-footer">
            <b-btn id="delete-confirm"
                   variant="primary"
                   @click="deleteGroup">
              Delete
            </b-btn>
            <b-btn id="delete-cancel"
                   variant="link"
                   @click="isModalOpen=false">
              Cancel
            </b-btn>
          </div>
        </b-modal>
      </div>
    </div>
  </div>
</template>

<script>
import { deleteCuratedGroup, renameCuratedGroup } from '@/api/curated';
import Loading from '@/mixins/Loading.vue';
import Validator from '@/mixins/Validator.vue';
import router from '@/router';

export default {
  name: 'CuratedGroupHeader',
  mixins: [Loading, Validator],
  props: ['curatedGroup'],
  data: () => ({
    isModalOpen: false,
    renameMode: {
      on: false,
      error: undefined,
      hideError: false,
      input: undefined
    }
  }),
  watch: {
    'renameMode.on': function() {
      if (this.renameMode.on) {
        this.$nextTick(() => {
          this.$refs.input.focus();
        });
      }
    }
  },
  mounted() {
    this.loaded();
  },
  methods: {
    enterRenameMode: function() {
      this.renameMode.input = this.curatedGroup.name;
      this.renameMode.on = true;
    },
    exitRenameMode: function() {
      this.renameMode.input = null;
      this.renameMode.on = false;
    },
    deleteGroup: function() {
      deleteCuratedGroup(this.curatedGroup.id)
        .then(() => {
          this.isModalOpen = false;
          router.push({ path: '/home' });
        })
        .catch(error => {
          this.error = error;
        });
    },
    rename: function() {
      this.renameMode.hideError = false;
      this.renameMode.error = this.validateCohortName({
        name: this.renameMode.input
      });
      if (!this.renameMode.error) {
        renameCuratedGroup(this.curatedGroup.id, this.renameMode.input).then(
          () => {
            this.curatedGroup.name = this.renameMode.input;
            this.exitRenameMode();
          }
        );
      }
    }
  }
};
</script>

<style scoped>
.modal-footer {
  border-top: none;
}
.modal-header {
  border-bottom: none;
}
</style>
