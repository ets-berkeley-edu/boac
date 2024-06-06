<template>
  <div class="py-0">
    <h3
      :id="headerId"
      class="font-size-24 font-weight-medium"
      :class="clazz"
      tabindex="0"
    >
      {{ text }}
      <slot />
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
