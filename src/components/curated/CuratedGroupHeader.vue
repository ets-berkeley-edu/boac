<template>
  <div class="d-flex justify-content-between mb-2">
    <div v-if="!renameMode">
      <h1 id="curated-group-name"
          class="page-section-header mt-0"
          tabindex="0"
          ref="pageHeader">
        <span>{{ curatedGroup.name || 'Curated Group' }}</span>
        <span class="faint-text"> (<span>{{ 'student' | pluralize(curatedGroup.studentCount, {1: 'One'})}}</span>)</span>
      </h1>
    </div>
    <div class="w-100 mr-3" v-if="renameMode">
      <div>
        <form @submit.prevent="rename">
          <input id="rename-input"
                 class="form-control"
                 v-model="renameInput"
                 @keyup.esc="exitRenameMode()"
                 :aria-invalid="!renameInput"
                 aria-label="Curated group name, 255 characters or fewer"
                 aria-required="true"
                 maxlength="255"
                 required
                 type="text"/>
        </form>
      </div>
      <div class="has-error mb-2" v-if="renameError">{{ renameError }}</div>
      <div class="faint-text mb-3">255 character limit <span v-if="size(renameInput)">({{255 - size(renameInput)}} left)</span></div>
      <div class="sr-only" aria-live="polite">{{ renameError }}</div>
      <div class="sr-only"
           aria-live="polite"
           v-if="size(renameInput) === 255">Name cannot exceed 255 characters.</div>
    </div>
    <div class="d-flex align-self-baseline mr-4" v-if="renameMode">
      <b-btn id="rename-confirm"
             class="btn-primary-color-override"
             variant="primary"
             size="sm"
             aria-label="Save changes to curated group name"
             @click.stop="rename"
             :disabled="!size(renameInput)">
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
    <div class="d-flex align-items-center mr-4" v-if="!renameMode">
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
import Loading from '@/mixins/Loading.vue';
import router from '@/router';
import Util from '@/mixins/Util';
import Validator from '@/mixins/Validator.vue';
import { deleteCuratedGroup, renameCuratedGroup } from '@/api/curated';

export default {
  name: 'CuratedGroupHeader',
  mixins: [Loading, Util, Validator],
  props: ['curatedGroup'],
  data: () => ({
    isModalOpen: false,
    renameError: undefined,
    renameInput: undefined,
    renameMode: false
  }),
  mounted() {
    this.loaded();
    this.putFocusNextTick('curated-group-name');
  },
  methods: {
    enterRenameMode: function() {
      this.renameInput = this.curatedGroup.name;
      this.renameMode = true;
      this.putFocusNextTick('rename-input');
    },
    exitRenameMode: function() {
      this.renameInput = undefined;
      this.renameMode = false;
      this.putFocusNextTick('curated-group-name');
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
      this.renameError = this.validateCohortName({
        name: this.renameInput
      });
      if (this.renameError) {
        this.putFocusNextTick('rename-input');
      } else {
        renameCuratedGroup(this.curatedGroup.id, this.renameInput).then(() => {
          this.curatedGroup.name = this.renameInput;
          this.exitRenameMode();
          this.putFocusNextTick('curated-group-name');
        });
      }
    }
  },
  watch: {
    renameInput: function() {
      this.renameError = undefined;
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
