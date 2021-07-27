<template>
  <div class="modal-header py-2">
    <h3 :id="headerId" class="font-size-24" tabindex="0">
      {{ text }}
      <slot></slot>
    </h3>
  </div>
</template>

<script>
export default {
  name: 'ModalHeader',
  props: {
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
  }
}
</script>
