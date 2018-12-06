<template>
  <div class="cohort-header-container">
    <div v-if="!renameMode.on">
      <h1 class="page-section-header">
        <span>{{ curatedGroup.name || 'Curated Group' }}</span>
        <span class="faint-text"> (<span>{{ 'student' | pluralize(curatedGroup.studentCount, {1: 'One'})}}</span>)</span>
      </h1>
    </div>
    <div class="cohort-rename-container" v-if="renameMode.on">
      <div>
        <form name="renameCohortForm" v-on:submit="rename">
          <input aria-required="true"
                 aria-label="Input cohort name, 255 characters or fewer"
                 :aria-invalid="!renameMode.input"
                 class="form-control"
                 @change="renameMode.hideError = true"
                 v-model="renameMode.input"
                 focus-on="renameMode.on"
                 id="rename-cohort-input"
                 maxlength="255"
                 name="name"
                 required
                 type="text"/>
        </form>
      </div>
      <div class="has-error"
           data-ng-bind="renameMode.error"
           data-ng-if="renameMode.error && !renameMode.hideError"></div>
      <div class="faint-text">255 character limit <span data-ng-if="renameMode.input.length">({{255 - renameMode.input.length}} left)</span></div>
    </div>
    <div class="curated-cohort-header-column-02">
      <div class="cohort-header-buttons no-wrap" v-if="renameMode.on">
        <button type="button"
                id="curated-cohort-rename"
                :aria-disabled="!renameMode.input"
                aria-label="Save changes to cohort name"
                class="btn btn-sm btn-primary cohort-manage-btn"
                @click.stop="rename"
                :disabled="!renameMode.input">
          Rename
        </button>
        <button type="button"
                aria-label="Cancel rename cohort"
                id="curated-cohort-rename-cancel"
                class="btn btn-sm btn-default cohort-manage-btn"
                @click="exitRenameMode">
          Cancel
        </button>
      </div>
      <div class="cohort-header-button-links no-wrap" v-if="!renameMode.on">
        <button type="button"
                id="rename-cohort-button"
                aria-label="Rename this cohort"
                class="btn-link cohort-manage-btn-link"
                @click="enterRenameMode">
          Rename
        </button>
        <span>
          <span class="faint-text">|</span>
          <b-btn v-b-modal="'myModal'"
                 id="delete-cohort-button"
                 aria-label="Delete this cohort"
                 class="btn-link cohort-manage-btn-link">
            Delete
          </b-btn>
        </span>
      </div>
    </div>
    <b-modal id="myModal"
             v-model="isModalOpen">
      <div class="modal-header" slot="modal-header">
        <h3 id="confirm-delete-header">Delete Curated Group</h3>
      </div>
      <div class="modal-body curated-cohort-label" id="confirm-delete-body">
        Are you sure you want to delete "<strong>{{ curatedGroup.name }}</strong>"?
      </div>
      <div class="modal-footer" slot="modal-footer">
        <b-btn variant="primary"
               @click="deleteGroup">
          Delete
        </b-btn>
        <b-btn variant="secondary"
               @click="isModalOpen=false">
          Cancel
        </b-btn>
      </div>
    </b-modal>
  </div>
</template>

<script>
import _ from 'lodash';
import { deleteCuratedGroup, renameCuratedGroup } from '@/api/cohorts';
import store from '@/store';

export default {
  name: 'CuratedGroupHeader',
  props: ['curatedGroup'],
  data: () => ({
    isModalOpen: false,
    renameMode: {
      on: false,
      error: undefined,
      input: undefined
    }
  }),
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
          this.$router.push('home');
        })
        .catch(error => {
          this.renameMode.error = error;
        });
    },
    rename: function() {
      // TODO: finish validation logic (BOAC-1496)
      if (_.isEmpty(this.renameMode.input)) {
        this.renameMode.error = 'Required';
      } else if (_.size(this.renameMode.input) > 255) {
        this.renameMode.error = 'Name must be 255 characters or fewer';
      }
      if (!this.renameMode.error) {
        renameCuratedGroup(this.curatedGroup.id, this.renameMode.input)
          .then(() => {
            this.curatedGroup.name = this.renameMode.input;
            store.commit('updateCuratedGroup', {
              id: this.curatedGroup.id,
              name: this.curatedGroup.name
            });
            this.exitRenameMode();
          })
          .catch(error => {
            this.renameMode.error = error;
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
