<template>
  <v-chip
    :aria-label="ariaLabel"
    class="pill-alert"
    :class="outlined ? '' : 'pill-color-override'"
    :color="color"
    density="comfortable"
    :variant="outlined ? 'outlined' : 'flat'"
  >
    <slot></slot>
  </v-chip>
</template>

<script>
export default {
  name: 'PillAlert',
  props: {
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
  }
}
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
