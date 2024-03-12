<template>
  <v-btn
    :id="id"
    :color="color"
    :disabled="disabled"
    @click.prevent="action"
  >
    <div class="d-flex align-baseline">
      <div v-if="inProgress" class="pr-1">
        <v-progress-circular indeterminate size="18" />
      </div>
      <span class="text-nowrap">
        <slot></slot>
      </span>
    </div>
  </v-btn>
</template>

<script>
export default {
  name: 'ProgressButton',
  props: {
    action: {
      type: Function,
      required: true
    },
    color: {
      default: 'primary',
      type: String,
      required: false
    },
    disabled: {
      type: Boolean,
      required: false
    },
    id: {
      type: String,
      required: true
    },
    inProgress: {
      type: Boolean,
      required: false
    }
  }
}
</script>
