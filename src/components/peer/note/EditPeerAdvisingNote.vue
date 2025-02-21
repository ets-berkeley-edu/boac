<template>
  <v-dialog
    v-if="mode"
    v-model="dialogModel"
    aria-labelledby="dialog-header-note"
    persistent
    scrollable
  >
    <v-card
      id="new-note-modal-container"
      class="modal-content"
      :class="{'modal-fullscreen': display.mdAndDown}"
      width="800"
      max-width="90%"
    >
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import {storeToRefs} from 'pinia'
import {useDisplay} from 'vuetify'
import {useNoteStore} from '@/stores/note-edit-session'

const dialogModel = defineModel<boolean>()
const display = useDisplay()
const {mode} = storeToRefs(useNoteStore())
</script>

<style scoped>

</style>
