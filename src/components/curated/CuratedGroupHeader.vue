<template>
  <div>
    <div class="d-flex justify-content-between mb-2">
      <div v-if="mode !== 'rename'">
        <h1
          id="curated-group-name"
          ref="pageHeader"
          class="page-section-header mt-0"
          tabindex="0">
          <span>{{ curatedGroupName || 'Curated Group' }}</span>
          <span v-if="!isNil(totalStudentCount)" class="faint-text"> (<span>{{ 'student' | pluralize(totalStudentCount, {1: '1'}) }}</span>)</span>
        </h1>
      </div>
      <div v-if="mode === 'rename'" class="w-100 mr-3">
        <div>
          <form @submit.prevent="rename">
            <input
              id="rename-input"
              v-model="renameInput"
              :aria-invalid="!renameInput"
              @keyup.esc="exitRenameMode()"
              class="form-control"
              aria-label="Curated group name, 255 characters or fewer"
              aria-required="true"
              maxlength="255"
              required
              type="text" />
          </form>
        </div>
        <div v-if="renameError" class="has-error mb-2">{{ renameError }}</div>
        <div class="faint-text m-2">255 character limit <span v-if="size(renameInput)">({{ 255 - size(renameInput) }} left)</span></div>
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
          :disabled="!size(renameInput)"
          @click.stop="rename"
          class="btn-primary-color-override"
          variant="primary"
          size="sm"
          aria-label="Save changes to curated group name">
          Rename
        </b-btn>
        <b-btn
          id="rename-cancel"
          @click="exitRenameMode"
          class="cohort-manage-btn"
          variant="link"
          aria-label="Cancel rename curated group"
          size="sm">
          Cancel
        </b-btn>
      </div>
      <div v-if="!mode" class="d-flex align-items-center mr-2">
        <div v-if="isOwnedByCurrentUser">
          <b-btn
            id="bulk-add-sids-button"
            @click="enterBulkAddMode"
            variant="link"
            aria-label="Add students to this curated group by entering a list of student IDs">
            Add Students
          </b-btn>
        </div>
        <div v-if="isOwnedByCurrentUser" class="faint-text">|</div>
        <div v-if="isOwnedByCurrentUser">
          <b-btn
            id="rename-button"
            @click="enterRenameMode"
            variant="link"
            aria-label="Rename this curated group">
            Rename
          </b-btn>
        </div>
        <div v-if="isOwnedByCurrentUser" class="faint-text">|</div>
        <div v-if="isOwnedByCurrentUser">
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
              Are you sure you want to delete "<strong>{{ curatedGroupName }}</strong>"?
            </div>
            <div slot="modal-footer">
              <b-btn
                id="delete-confirm"
                @click="deleteGroup"
                class="btn-primary-color-override"
                variant="primary">
                Delete
              </b-btn>
              <b-btn
                id="delete-cancel"
                @click="isModalOpen=false"
                variant="link">
                Cancel
              </b-btn>
            </div>
          </b-modal>
        </div>
        <div v-if="isOwnedByCurrentUser" class="faint-text">|</div>
        <div>
          <b-btn
            id="export-student-list-button"
            :disabled="!exportEnabled || !totalStudentCount"
            v-b-modal="'export-list-modal'"
            variant="link"
            aria-label="Download CSV file containing all students">
            Export List
          </b-btn>
          <b-modal
            id="export-list-modal"
            v-model="showExportListModal"
            @shown="focusModalById('export-list-confirm')"
            body-class="pl-0 pr-0"
            hide-footer
            hide-header>
            <ExportListModal
              :cancel-export-list-modal="cancelExportGroupModal"
              :export-list="exportGroup" />
          </b-modal>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import CuratedEditSession from '@/mixins/CuratedEditSession';
import ExportListModal from '@/components/util/ExportListModal';
import Loading from '@/mixins/Loading.vue';
import router from '@/router';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import Validator from '@/mixins/Validator.vue';
import { deleteCuratedGroup, downloadCuratedGroupCsv } from '@/api/curated';

export default {
  name: 'CuratedGroupHeader',
  components: { ExportListModal },
  mixins: [Context, CuratedEditSession, Loading, UserMetadata, Util, Validator],
  data: () => ({
    exportEnabled: true,
    isModalOpen: false,
    renameError: undefined,
    renameInput: undefined,
    showExportListModal: false
  }),
  computed: {
    isOwnedByCurrentUser() {
      return this.ownerId === this.user.id;
    }
  },
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
    cancelExportGroupModal() {
      this.showExportListModal = false;
      this.alertScreenReader(`Cancel export of ${this.name} curated group`);
    },
    enterBulkAddMode() {
      this.setMode('bulkAdd');
    },
    enterRenameMode() {
      this.renameInput = this.curatedGroupName;
      this.setMode('rename');
      this.putFocusNextTick('rename-input');
    },
    exitRenameMode() {
      this.renameInput = undefined;
      this.setMode(undefined);
      this.putFocusNextTick('curated-group-name');
    },
    deleteGroup() {
      deleteCuratedGroup(this.curatedGroupId)
        .then(() => {
          this.isModalOpen = false;
          router.push({ path: '/home' });
        })
        .catch(error => {
          this.error = error;
        });
    },
    exportGroup(csvColumnsSelected) {
      this.showExportListModal = false
      this.exportEnabled = false;
      this.alertScreenReader(`Exporting ${this.name} curated group`);
      downloadCuratedGroupCsv(this.curatedGroupId, this.curatedGroupName, csvColumnsSelected).then(() => {
        this.exportEnabled = true;
      });
    },
    rename() {
      this.renameError = this.validateCohortName({
        name: this.renameInput
      });
      if (this.renameError) {
        this.putFocusNextTick('rename-input');
      } else {
        this.renameCuratedGroup(this.renameInput).then(() => {
          this.setPageTitle(this.renameInput);
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
