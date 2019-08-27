<template>
  <div class="d-flex align-items-end pt-2 mb-1" :class="{'mt-2': undocked}">
    <div class="flex-grow-1 new-note-header font-weight-bolder">
      <span v-if="mode === 'editTemplate'">Edit Template</span>
      <span v-if="mode !== 'editTemplate'">New Note</span>
    </div>
    <div v-if="undocked" class="mr-4">
      <b-dropdown
        v-if="mode !== 'editTemplate'"
        id="my-templates-button"
        text="Templates"
        aria-label="Select a note template"
        variant="primary"
        class="mb-2 ml-0"
        right>
        <b-dropdown-header v-if="!size(noteTemplates)" id="no-templates-header">
          <div class="font-weight-bolder">Templates</div>
          <div>
            <div class="font-weight-bolder">You have no saved templates.</div>
            <div>To begin, create a new note and select, "Save note as template," to build your first note template.</div>
          </div>
        </b-dropdown-header>
        <b-dropdown-item
          v-for="template in noteTemplates"
          :id="`note-template-${template.id}`"
          :key="template.id">
          <div class="align-items-center d-flex justify-content-between">
            <div>
              <b-btn variant="link" class="dropdown-item p-0" @click="loadTemplate(template)">{{ truncate(template.title) }}</b-btn>
            </div>
            <div class="align-items-center d-flex ml-2 no-wrap">
              <div>
                <b-btn variant="link" class="p-0" @click="editTemplate(template)">Edit</b-btn>
              </div>
              <div>
                |
              </div>
              <div>
                <b-btn variant="link" class="p-0" @click="deleteTemplate(template.id)">Delete</b-btn>
              </div>
            </div>
          </div>
        </b-dropdown-item>
      </b-dropdown>
    </div>
    <div v-if="!undocked" class="pr-0">
      <label id="minimize-button-label" class="sr-only">Minimize the create note dialog box</label>
      <b-btn
        id="minimize-new-note-modal"
        variant="link"
        aria-labelledby="minimize-button-label"
        class="pr-2"
        @click.prevent="minimize()">
        <span class="sr-only">Minimize</span>
        <font-awesome icon="window-minimize" class="minimize-icon text-dark" />
      </b-btn>
    </div>
    <div v-if="!undocked" class="pr-2">
      <label id="cancel-button-label" class="sr-only">Cancel the create-note form</label>
      <b-btn
        id="cancel-new-note-modal"
        variant="link"
        aria-labelledby="cancel-button-label"
        class="pl-1 pb-1"
        @click.prevent="cancel()">
        <span class="sr-only">Cancel</span>
        <font-awesome icon="times" class="fa-icon-size text-dark" />
      </b-btn>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import NoteEditSession from '@/mixins/NoteEditSession';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'NewNotePageHeader',
  mixins: [Context, NoteEditSession, UserMetadata, Util],
  props: {
    cancel: {
      required: true,
      type: Function
    },
    deleteTemplate: {
      required: true,
      type: Function
    },
    editTemplate: {
      required: true,
      type: Function
    },
    loadTemplate: {
      required: true,
      type: Function
    },
    minimize: {
      required: true,
      type: Function
    },
    undocked: {
      required: true,
      type: Boolean
    }
  }
}
</script>

<style scoped>
.fa-icon-size {
  font-size: 28px;
}
.minimize-icon {
  font-size: 24px;
}
.new-note-header {
  font-size: 24px;
  margin: 0 15px 6px 15px;
}
</style>
