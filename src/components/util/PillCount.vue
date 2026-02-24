<template>
  <div
    :id="id"
    class="pill-count rounded-xl"
    :class="`bg-${color}`"
  >
    <slot />
  </div>
</template>

<script setup>
defineProps({
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

<style lang="scss">
.pill-count {
  border-color: rgba(var(--v-border-color), var(--v-border-opacity)) !important;
  border-style: solid !important;
  border-width: 1px !important;
  font-size: 16px !important;
  font-weight: 800;
  line-height: 1rem;
  padding-top: 1px;
}
</style>
