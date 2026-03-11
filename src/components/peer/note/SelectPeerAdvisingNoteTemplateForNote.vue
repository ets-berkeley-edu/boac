<template>
  <div>
    <v-menu
      v-if="noteStore.mode !== 'editTemplate'"
      id="peer-advising-note-templates-menu"
      absolute
      attach="#peer-advising-note-modal-header"
      :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
      eager
      location="bottom end"
      no-click-animation
      :width="noteTemplates.length ? 500 : 350"
      @update:model-value="onToggleTemplatesMenu"
    >
      <template #activator="{props: menuProps}">
        <v-btn
          id="peer-advising-note-templates-button"
          class="ml-auto"
          color="primary"
          :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
          flat
          v-bind="menuProps"
        >
          <div class="pr-1">Templates</div>
          <v-icon :icon="mdiMenuDown" size="24" />
        </v-btn>
      </template>
      <v-list
        v-if="noteTemplates.length"
        aria-label="note templates"
        variant="flat"
      >
        <v-list-item
          v-for="template in noteTemplates"
          :id="`load-note-template-${template.id}`"
          :key="template.id"
          :aria-label="`Use template &quot;${template.title}&quot;`"
          class="font-size-15 font-weight-550 px-3 text-primary"
          :disabled="isSaving"
          @click="loadTemplate(template)"
        >
          <div class="truncate-with-ellipsis">{{ template.title }}</div>
        </v-list-item>
      </v-list>
      <v-list v-if="!noteTemplates.length">
        <v-list-item disabled>
          <span v-if="!isNoteTemplatesLoading" class="font-size-16 font-weight-medium">You have no saved templates.</span>
          <span v-if="isNoteTemplatesLoading" class="font-size-16 font-weight-medium">Loading Note Templates...</span>
        </v-list-item>
      </v-list>
    </v-menu>
    <v-btn
      v-if="noteStore.mode === 'editDraft'"
      aria-label="Close dialog"
      class="d-flex align-self-center"
      height="36"
      :icon="mdiClose"
      size="large"
      variant="text"
      width="36"
      @click="props.exit"
    />
  </div>
</template>

<script setup lang="ts">
import {size} from 'lodash'
import {mdiClose, mdiMenuDown} from '@mdi/js'
import {storeToRefs} from 'pinia'
import type {NoteTemplate} from '@/lib/types'
import {alertScreenReader} from '@/lib/utils'
import {useNoteStore} from '@/stores/note-edit-session'

const emit = defineEmits([
  'template-selected'
])

const props = defineProps({
  noteTemplates: {
    required: true,
    type: Array<NoteTemplate>
  },
  exit: {
    type: Function,
    required: true
  },
  isNoteTemplatesLoading: {
    required: true,
    type: Boolean
  }
})

const noteStore = useNoteStore()
const {isSaving} = storeToRefs(noteStore)

const loadTemplate = (template: NoteTemplate) => {
  emit('template-selected', template)
}

const onToggleTemplatesMenu = (isOpen: boolean) => {
  if (isOpen) {
    const count = size(props.noteTemplates)
    const suffix = count === 1 ? 'one saved template' : `${count || 'no'} saved templates`
    alertScreenReader(`You have ${suffix}.`)
  }
}
</script>
