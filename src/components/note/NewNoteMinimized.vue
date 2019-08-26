<template>
  <div class="minimized-placeholder d-flex align-items-end ml-3 mr-3">
    <div class="flex-grow-1 minimized-label">
      New Note
    </div>
    <div class="pr-0">
      <b-btn
        id="maximize-new-note-modal"
        aria-label="Bring create-note form into view"
        variant="link"
        class="pr-2"
        @click.stop="maximize()">
        <span class="sr-only">Maximize</span>
        <font-awesome icon="window-maximize" class="fa-icon-size text-white" />
      </b-btn>
    </div>
    <div class="pr-2 pt-1">
      <b-btn
        id="cancel-minimized-new-note"
        aria-label="Cancel the create-note form"
        variant="link"
        class="pl-1"
        @click.prevent="cancel()">
        <span class="sr-only">Cancel</span>
        <font-awesome icon="times" class="fa-icon-size text-white" />
      </b-btn>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import NoteEditSession from '@/mixins/NoteEditSession';
import Util from '@/mixins/Util';

export default {
  name: 'NewNoteMinimized',
  mixins: [Context, NoteEditSession, Util],
  props: {
    cancel: Function
  },
  methods: {
    maximize() {
      this.setNoteMode('docked');
      this.alertScreenReader("Create note form is visible.");
      this.putFocusNextTick('create-note-subject');
    }
  }
}
</script>

<style scoped>
.minimized-placeholder {
  background-color: #125074;
  border: 1px solid #aaa;
  bottom: 0;
  box-shadow: 0 0 10px #ccc;
  color: #fff;
  height: 50px;
  position: fixed;
  right: 10px;
  width: 30%;
  z-index: 2;
}
.minimized-label {
  font-size: 24px;
  margin: 0 15px 12px 15px;
}
</style>
