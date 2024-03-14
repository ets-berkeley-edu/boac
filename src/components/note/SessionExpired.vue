<template>
  <div class="text-medium-emphasis">
    <h4 class="font-size-18 mb-1">
      <v-icon :icon="mdiAlert" class="pr-1 text-warning" />
      Uh oh, your session timed out!
    </h4>
    <div>
      To continue, you will need to refresh the page and reauthenticate via CalNet. Your edits will be lost unless you
      copy them to a text editor or the clipboard and paste or reenter them when the page reloads.
    </div>
    <div class="pb-2 pt-1">
      Thank you.
    </div>
  </div>
</template>

<script setup>
import {mdiAlert} from '@mdi/js'
</script>

<script>
export default {
  name: 'SessionExpired'
}
</script>
