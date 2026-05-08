<template>
  <div class="indicators d-flex ml-auto">
    <div v-if="size(message.attachments)" class="mr-auto">
      <v-icon :aria-hidden="true" color="info" :icon="mdiPaperclip" />
      <span class="sr-only">Has attachments.</span>
    </div>
    <v-badge
      v-if="size(message.comments)"
      class="ml-auto mr-2 mt-1"
      color="info"
      :content="size(message.comments)"
      :label="`${pluralize('comment', size(message.comments))}.`"
    >
      <v-icon
        :aria-hidden="true"
        color="info"
        :icon="mdiCommentOutline"
        size="1.4rem"
      />
    </v-badge>
  </div>
</template>

<script setup lang="ts">
import {mdiCommentOutline, mdiPaperclip} from '@mdi/js'
import {size} from 'lodash'
import {pluralize} from '@/lib/utils'

defineProps({
  message: {
    required: true,
    type: Object
  }
})
</script>

<style scoped>
.indicators {
  min-width: 3.25rem;
  width: 3.25rem;
}
</style>
