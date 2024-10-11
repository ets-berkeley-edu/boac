<template>
  <v-chip
    :id="id"
    :aria-label="ariaLabel"
    class="bg-white font-weight-bold my-1 text-medium-emphasis text-no-wrap text-uppercase pill-item v-chip-content-override"
    :class="clazz"
    density="comfortable"
    :disabled="disabled"
    :href="href"
    :prepend-icon="icon"
    variant="outlined"
  >
    <slot />
    <template #append>
      <v-btn
        v-if="closable"
        :id="`remove-${id}-btn`"
        :aria-label="`Remove ${name} ${label}`"
        color="error"
        density="compact"
        :disabled="disabled"
        :icon="mdiCloseCircle"
        title="Remove"
        variant="text"
        @click.stop.prevent="$emit('close-clicked')"
      />
    </template>
  </v-chip>
</template>

<script setup>
import {mdiCloseCircle} from '@mdi/js'

defineEmits('close-clicked')

defineProps({
  ariaLabel: {
    default: undefined,
    required: false,
    type: String
  },
  clazz: {
    default: undefined,
    required: false,
    type: [Object, String]
  },
  closable: {
    required: false,
    type: Boolean
  },
  disabled: {
    required: false,
    type: Boolean
  },
  href: {
    default: undefined,
    required: false,
    type: String
  },
  icon: {
    default: undefined,
    required: false,
    type: String
  },
  id: {
    required: true,
    type: String
  },
  label: {
    default: '',
    required: false,
    type: String
  },
  name: {
    default: '',
    required: false,
    type: String
  },
  onClickClose: {
    default: () => {},
    required: false,
    type: Function
  }
})
</script>

<style scoped>
.pill-item {
  padding: 0 2px 0 12px;
}
</style>
