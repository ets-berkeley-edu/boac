<template>
  <div class="modal-header py-2">
    <h3
      :id="headerId"
      class="font-size-24"
      :class="clazz"
      tabindex="0"
    >
      {{ text }}
      <slot></slot>
    </h3>
  </div>
</template>

<script>
export default {
  name: 'ModalHeader',
  props: {
    clazz: {
      default: '',
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
  }
}
</script>

<style scoped>
.modal-header {
  align-items: flex-start;
  display: flex;
  justify-content: space-between;
  padding: 1rem 1rem;
}
</style>
