<template>
  <h2
    :id="headerId"
    class="mx-2"
    :class="clazz"
  >
    {{ text }}
    <slot />
  </h2>
</template>

<script setup>
defineProps({
  clazz: {
    default: 'font-size-24 font-weight-medium',
    required: false,
    type: String
  },
  headerId: {
    default: 'modal-header',
    required: false,
    type: String
  },
  text: {
    default: '',
    required: false,
    type: String
  }
})
</script>
