<template>
  <div>
    <div class="d-flex justify-content-between mb-2">
      <div v-if="mode !== 'rename'">
        <h1
          id="curated-group-name"
          ref="pageHeader"
          class="page-section-header mt-0"
          tabindex="0">
          <span>{{ curatedGroup.name || 'Curated Group' }}</span>
          <span class="faint-text"> (<span>{{ 'student' | pluralize(curatedGroup.studentCount, {1: '1'}) }}</span>)</span>
        </h1>
      </div>
      <div v-if="mode === 'rename'" class="w-100 mr-3">
        <div>
          <form @submit.prevent="rename">
            <input
              id="rename-input"
              v-model="renameInput"
              class="form-control"
              :aria-invalid="!renameInput"
              aria-label="Curated group name, 255 characters or fewer"
              aria-required="true"
              maxlength="255"
              required
              type="text"
              @keyup.esc="exitRenameMode()" />
          </form>
        </div>
        <div v-if="renameError" class="has-error mb-2">{{ renameError }}</div>
        <div class="faint-text mb-3">255 character limit <span v-if="size(renameInput)">({{ 255 - size(renameInput) }} left)</span></div>
        <div class="sr-only" aria-live="polite">{{ renameError }}</div>
        <div
          v-if="size(renameInput) === 255"
          class="sr-only"
          aria-live="polite">
          Name cannot exceed 255 characters.
        </div>
      </div>
      <div v-if="mode === 'rename'" class="d-flex align-self-baseline mr-4">
        <b-btn
          id="rename-confirm"
          class="btn-primary-color-override"
          variant="primary"
          size="sm"
          aria-label="Save changes to curated group name"
          :disabled="!size(renameInput)"
          @click.stop="rename">
          Rename
        </b-btn>
        <b-btn
          id="rename-cancel"
          class="cohort-manage-btn"
          variant="link"
          aria-label="Cancel rename curated group"
          size="sm"
          @click="exitRenameMode">
          Cancel
        </b-btn>
      </div>
      <div v-if="!mode" class="d-flex align-items-center mr-4">
        <div>
          <b-btn
            id="bulk-add-sids-button"
            variant="link"
            aria-label="Add students to this curated group by entering a list of student IDs"
            @click="enterBulkAddMode">
            Add Students
          </b-btn>
        </div>
        <div class="faint-text">|</div>
        <div>
          <b-btn
            id="rename-button"
            variant="link"
            aria-label="Rename this curated group"
            @click="enterRenameMode">
            Rename
          </b-btn>
        </div>
        <div class="faint-text">|</div>
        <div>
          <b-btn
            id="delete-button"
            v-b-modal="'myModal'"
            variant="link"
            aria-label="Delete this curated group">
            Delete
          </b-btn>
          <b-modal
            id="myModal"
            v-model="isModalOpen">
            <div slot="modal-header">
              <h3>Delete Curated Group</h3>
            </div>
            <div id="confirm-delete-body" class="modal-body curated-cohort-label">
              Are you sure you want to delete "<strong>{{ curatedGroup.name }}</strong>"?
            </div>
            <div slot="modal-footer">
              <b-btn
                id="delete-confirm"
                class="btn-primary-color-override"
                variant="primary"
                @click="deleteGroup">
                Delete
              </b-btn>
              <b-btn
                id="delete-cancel"
                variant="link"
                @click="isModalOpen=false">
                Cancel
              </b-btn>
            </div>
          </b-modal>
        </div>
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
  props: {
    'curatedGroup': Object,
    'mode': String,
    'setMode': Function
  },
  data: () => ({
    isModalOpen: false,
    renameError: undefined,
    renameInput: undefined
  }),
  watch: {
    renameInput() {
      this.renameError = undefined;
    }
  },
  mounted() {
    this.loaded();
    this.putFocusNextTick('curated-group-name');
  },
  methods: {
    enterBulkAddMode() {
      this.setMode('bulkAdd');
    },
    enterRenameMode() {
      this.renameInput = this.curatedGroup.name;
      this.setMode('rename');
      this.putFocusNextTick('rename-input');
    },
    exitRenameMode() {
      this.renameInput = undefined;
      this.setMode(undefined);
      this.putFocusNextTick('curated-group-name');
    },
    deleteGroup() {
      deleteCuratedGroup(this.curatedGroup.id)
        .then(() => {
          this.isModalOpen = false;
          router.push({ path: '/home' });
        })
        .catch(error => {
          this.error = error;
        });
    },
    rename() {
      this.renameError = this.validateCohortName({
        name: this.renameInput
      });
      if (this.renameError) {
        this.putFocusNextTick('rename-input');
      } else {
        renameCuratedGroup(this.curatedGroup.id, this.renameInput).then(() => {
          this.curatedGroup.name = this.renameInput;
          this.setPageTitle(this.curatedGroup.name);
          this.exitRenameMode();
          this.putFocusNextTick('curated-group-name');
        });
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
