<template>
  <div class="align-center d-flex">
    <label
      class="mr-3"
      for="my-notes-only-toggle"
    >
      <span class="font-weight-bold mr-2">Show:</span>
      <span :class="{'text-medium-emphasis': showMyNotesOnly || isFetchingNotes}">All Notes</span>
    </label>
    <div>
      <v-switch
        id="my-notes-only-toggle"
        v-model="showMyNotesOnly"
        :class="{'text-medium-emphasis': !showMyNotesOnly}"
        class="switch"
        color="indigo"
        density="compact"
        :disabled="isFetchingNotes"
        hide-details
        label="My Notes"
      />
    </div>
    <SectionSpinner :loading="isFetchingNotes" />
  </div>
</template>

<script setup lang="ts">
import SectionSpinner from '@/components/util/SectionSpinner.vue'

const showMyNotesOnly = defineModel<boolean>()

defineProps({
  isFetchingNotes: {
    required: true,
    type: Boolean
  }
})
</script>
