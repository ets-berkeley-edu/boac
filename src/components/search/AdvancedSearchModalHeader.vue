<template>
  <div class="align-center d-flex justify-space-between">
    <ModalHeader
      header-id="advanced-search-header"
      text="Advanced Search"
    />
    <v-btn
      id="advanced-search-close"
      aria-label="Close Advanced Search dialog"
      class="font-size-14 font-weight-bold"
      density="comfortable"
      elevation="0"
      icon
      title="Close"
      @click="onClickClose"
      @keydown.enter="onClickClose"
    >
      <v-icon
        color="primary"
        :icon="mdiCloseThick"
        size="16"
      />
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import ModalHeader from '@/components/util/ModalHeader.vue'
import {mdiCloseThick} from '@mdi/js'

defineProps({
  onClickClose: {
    required: true,
    type: Function
  }
})
</script>
