<template>
  <div class="d-flex justify-space-between">
    <div>
      <ModalHeader :text="headerText" />
    </div>
    <div>
      <SelectNoteTemplateForNote :exit="noop" />
    </div>
  </div>
</template>

<script setup lang="ts">
import {noop} from 'lodash'
import ModalHeader from '@/components/util/ModalHeader.vue'
import SelectNoteTemplateForNote from '@/components/note/template/SelectNoteTemplateForNote.vue'

defineProps({
  headerText: {
    required: true,
    type: String
  }
})
</script>
