<template>
  <v-btn
    :id="id"
    :color="color"
    :disabled="disabled"
    size="large"
    @click.prevent="action"
  >
    <div class="align-center d-flex">
      <div v-if="inProgress" class="pr-1">
        <v-progress-circular indeterminate size="16" width="2" />
      </div>
      <div class="text-no-wrap">
        <slot />
      </div>
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
