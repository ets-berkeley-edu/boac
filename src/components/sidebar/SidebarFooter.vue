<template>
  <div
    class="bg-tertiary px-3 py-0 w-100"
    :class="{'fixed-bottom-sidebar': $vuetify.display.mdAndUp, 'z-index-0': !loading}"
  >
    <LinkToDraftNotes class="pt-2" :class="{'pb-3': currentUser.isAdmin}" />
    <v-btn
      v-if="!currentUser.isAdmin"
      id="batch-note-button"
      class="mb-5 mt-3 w-100"
      color="primary"
      :disabled="!!useNoteStore().mode"
      variant="flat"
      @click="isCreateNoteModalOpen = true"
    >
      <v-icon class="mr-1" :icon="mdiFileDocument" />
      New Note
    </v-btn>
    <EditBatchNoteModal
      v-model="isCreateNoteModalOpen"
      initial-mode="createBatch"
      :on-close="() => {
        isCreateNoteModalOpen = false
        putFocusNextTick('batch-note-button')
      }"
      :toggle-show="show => isCreateNoteModalOpen = show"
    />
  </div>
</template>

<script setup>
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal'
import LinkToDraftNotes from '@/components/sidebar/LinkToDraftNotes'
import {mdiFileDocument} from '@mdi/js'
import {putFocusNextTick} from '@/lib/utils'
import {ref} from 'vue'
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const currentUser = useContextStore().currentUser
const isCreateNoteModalOpen = ref(false)
const {loading} = storeToRefs(useContextStore())
</script>

<style scoped>
.fixed-bottom-sidebar {
  bottom: 0;
  box-shadow: 0px -25px 35px -22px rgb(var(--v-theme-tertiary));
  position: fixed;
  z-index: 2;
}</style>
