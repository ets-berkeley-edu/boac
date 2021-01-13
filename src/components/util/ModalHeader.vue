<template>
  <div class="modal-header" :class="containerClass">
    <h3 id="modal-header" class="font-size-24" tabindex="0">
      {{ text }}
      <slot></slot>
    </h3>
  </div>
</template>

<script>
export default {
  name: 'ModalHeader',
  props: {
    containerClass: {
      default: undefined,
      required: false,
      type: String
    },
    text: {
      default: '',
      required: false,
      type: String
    }
  }
}
</script>
