<template>
  <v-chip
    :id="id"
    :aria-label="ariaLabel"
    class="border-sm pill-count"
    :class="{'pill-color-override': outlined}"
    :color="color"
    density="comfortable"
    :variant="outlined ? 'outlined' : 'flat'"
  >
    <slot />
  </v-chip>
</template>

<script setup>
defineProps({
  ariaLabel: {
    default: undefined,
    required: false,
    type: String
  },
  color: {
    default: 'surface-variant',
    required: false,
    type: String
  },
  id: {
    required: true,
    type: String
  },
  outlined: {
    required: false,
    type: Boolean
  }
})
</script>

<style lang="scss" scoped>
.pill-count {
  font-size: 16px !important;
  font-weight: 800;
  min-width: fit-content;
  padding: 0 12px 1px;
}
.pill-color-override {
  color: rgb(var(--v-theme-surface)) !important;
}
</style>
