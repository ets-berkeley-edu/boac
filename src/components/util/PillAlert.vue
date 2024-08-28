<template>
  <v-chip
    :aria-label="ariaLabel"
    class="pill-alert"
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
    required: true,
    type: String
  },
  color: {
    default: 'surface',
    required: false,
    type: String
  },
  outlined: {
    required: false,
    type: Boolean
  }
})
</script>

<style lang="scss" scoped>
.pill-alert {
  background-color: #fff;
  font-size: 16px !important;
  font-weight: 800;
  padding: 0 12px 1px !important;
}
.pill-color-override {
  color: #fff !important;
}
</style>
