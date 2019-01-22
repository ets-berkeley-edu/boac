<template>
  <div class="container-manage-cohorts">
    <Spinner/>
    <div v-if="!loading">
      <h1 ref="pageHeader" tabindex="0" class="page-section-header">Manage Curated Groups</h1>
      <div v-if="!curatedGroups.length" data-ng-controller="CreateCuratedCohortController">
        You have no curated groups.
        <a id="curated-group-create"
           href
           data-ng-click="openCreateCuratedCohortModal()"><i class="fas fa-plus"></i> Create a new curated group</a>
      </div>
      <div v-for="(group, index) in curatedGroups" v-bind:key="group.id">
        <hr class="cohort-manage-row-separator"/>
        <v-layout row v-if="!group.editMode">
          <div class="cohort-manage-name">
            <strong>
              <router-link :id="`curated-group-name-${index}`"
                           :to="'/cohort/curated/' + group.id">{{ group.name }}</router-link>
            </strong>
            <span class="faint-text">(<span :id="`curated-group-student-count-${index}`">{{ group.studentCount }}</span>)</span>
          </div>
          <div>
            <span data-ng-controller="DeleteCuratedCohortController">
              <button type="button"
                      :id="`delete-curated-group-btn-${index}`"
                      class="btn-link cohort-manage-btn-link"
                      data-ng-click="openDeleteCuratedCohortModal(group)">
                Delete
              </button> <span class="faint-text">|</span>
            </span>
            <button type="button"
                    :id="`edit-curated-group-btn-${index}`"
                    class="btn-link cohort-manage-btn-link"
                    data-ng-click="setEditMode(group, true)">
              Rename
            </button>
          </div>
        </v-layout>
        <form name="renameCuratedCohortForm"
              class="flex-container flex-space-between cohort-manage-row"
              v-on:click="rename(group, group.name)"
              v-if="group.editMode">
          <div class="cohort-manage-text-input">
            <input aria-required="true"
                   class="form-control"
                   data-ng-change="group.hideError = true"
                   v-model="group.name"
                   :v-focus-if="group.editMode"
                   :id="`curated-group-label-input-${index}`"
                   maxlength="255"
                   name="label"
                   required
                   type="text"/>
            <div class="has-error" data-ng-bind="" data-ng-if="group.error && !group.hideError">{{ group.error }}</div>
            <div class="faint-text">255 character limit <span v-if="group.name.length">({{255 - group.name.length}} left)</span></div>
          </div>
          <div class="edit-mode-button-container">
            <button type="button"
                    :id="`curated-group-save-btn-${index}`"
                    class="btn btn-sm btn-primary cohort-manage-btn"
                    v-disabled="!group.name"
                    v-on:click="rename(group, group.name)">
              Rename
            </button>
            <button type="button"
                    :id="`curated-group-cancel-btn-${index}`"
                    class="btn btn-sm btn-default cohort-manage-btn"
                    v-on:click="cancelEdit(group)">
              Cancel
            </button>
          </div>
        </form>
        <hr class="cohort-manage-row-separator" v-if="index === curatedGroups.length - 1"/>
      </div>
    </div>
  </div>
</template>

<script>
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import store from '@/store';

export default {
  name: 'Manage',
  mixins: [Loading],
  components: { Spinner },
  computed: {
    curatedGroups() {
      this.loaded();
      return store.getters['curated/myCuratedGroups'];
    }
  }
};
</script>

<style scoped>
.cohort-manage-btn {
  height: 38px;
  margin: 0 0 0 5px;
}
.cohort-manage-btn-link {
  padding: 1px 0 1px 0;
}
.cohort-manage-name {
  padding-left: 10px;
  width: 70%;
}
.cohort-manage-text-input {
  flex: 1;
  min-width: 200px;
  padding-left: 10px;
}
.cohort-manage-row {
  flex-flow: wrap;
  padding: 10px 10px 5px 0;
}
.cohort-manage-row div:first-child {
  margin-right: 10px;
}
.cohort-manage-row-separator {
  margin: 10px 0 10px 0;
}
</style>
