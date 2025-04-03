<template>
  <div>
    <v-menu
      v-if="noteStore.mode !== 'editTemplate'"
      id="templates-menu"
      absolute
      attach="#edit-note-header"
      :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
      location="bottom end"
      no-click-animation
      :width="noteTemplates.length ? 500 : 350"
      @update:model-value="onToggleTemplatesMenu"
    >
      <template #activator="{props: menuProps}">
        <v-btn
          id="my-templates-button"
          class="ml-auto mr-2"
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
        class="scrollbar-gutter-stable"
        variant="flat"
      >
        <v-list-item-action v-for="template in noteTemplates" :key="template.id">
          <v-container class="pa-2" fluid>
            <v-row class="align-center d-flex flex-nowrap" no-gutters>
              <v-col class="py-0" cols="8">
                <button
                  :id="`load-note-template-${template.id}`"
                  :aria-label="`Use template &quot;${template.title}&quot;`"
                  class="d-flex font-size-15 font-weight-550 load-note-template-btn justify-start pl-4 text-primary"
                  :disabled="isSaving"
                  :title="template.title"
                  @click="loadTemplate(template)"
                >
                  <div class="truncate-with-ellipsis">{{ template.title }}</div>
                </button>
              </v-col>
            </v-row>
          </v-container>
        </v-list-item-action>
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
import {alertScreenReader} from '@/lib/utils'
import {useNoteStore} from '@/stores/note-edit-session'

const emit = defineEmits([
  'template-selected'
])

const props = defineProps({
  noteTemplates: {
    required: true,
    type: Array
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

const loadTemplate = template => {
  emit('template-selected', template)
}

const onToggleTemplatesMenu = isOpen => {
  if (isOpen) {
    const count = size(props.noteTemplates)
    const suffix = count === 1 ? 'one saved template' : `${count || 'no'} saved templates`
    alertScreenReader(`You have ${suffix}.`)
  }
}

</script>

<style scoped>
.load-note-template-btn {
  width: 460px;
}
</style>
