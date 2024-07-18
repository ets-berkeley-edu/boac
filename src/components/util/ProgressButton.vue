<template>
  <v-btn
    :id="id"
    :color="color"
    :disabled="disabled"
    :size="size"
    :variant="variant"
    @click.prevent="action"
  >
    <div class="align-center d-flex text-no-wrap">
      <div v-if="inProgress" class="mr-2">
        <v-progress-circular indeterminate size="16" width="2" />
      </div>
      <div>
        {{ text }}
        <slot />
      </div>
    </div>
  </v-btn>
</template>

<script setup>
defineProps({
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
  },
  size: {
    default: 'default',
    type: [String, Number],
    required: false
  },
  text: {
    default: undefined,
    type: String,
    required: false
  },
  variant: {
    default: 'flat',
    type: String,
    required: false
  }
})
</script>
