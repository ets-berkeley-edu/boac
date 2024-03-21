<template>
  <div class="align-center d-flex justify-space-between">
    <h2
      id="advanced-search-header"
      class="font-size-24 font-weight-700"
      tabindex="-1"
    >
      Advanced Search
    </h2>
    <div>
      <v-btn
        id="advanced-search-close"
        class="font-size-14 font-weight-700"
        elevation="0"
        icon
        @click="onClickClose"
        @keydown.enter="onClickClose"
      >
        <span class="sr-only">Close</span>
        <v-icon
          color="primary"
          :icon="mdiCloseThick"
          size="16"
        />
      </v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import {mdiCloseThick} from '@mdi/js'

defineProps({
  onClickClose: {
    required: true,
    type: Function
  }
})
</script>
