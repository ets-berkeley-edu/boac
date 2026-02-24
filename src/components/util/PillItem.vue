<template>
  <div
    :id="id"
    :aria-label="ariaLabel"
    class="pill-item rounded-pill text-medium-emphasis text-no-wrap text-uppercase"
    :class="{'text-anchor': href}"
  >
    <component
      :is="href ? 'a' : 'span'"
      class="align-center d-flex truncate-with-ellipsis"
      :class="{
        'cursor-pointer': href,
        'mr-2': closable
      }"
      :disabled="disabled"
      :download="!!href"
      :href="href"
    >
      <v-icon
        v-if="icon"
        class="mr-2"
        :icon="icon"
        size="1.125rem"
      />
      <slot />
    </component>
    <v-btn
      v-if="closable"
      :id="`remove-${id}-btn`"
      :aria-label="`Remove ${name} ${label}`"
      class="ml-auto"
      color="error"
      :disabled="disabled"
      :icon="mdiCloseCircle"
      size="1.5rem"
      variant="text"
      @click.stop.prevent="emit('closeClicked')"
    />
  </div>
</template>

<script setup>
import {mdiCloseCircle} from '@mdi/js'

const emit = defineEmits(['closeClicked'])

defineProps({
  ariaLabel: {
    default: undefined,
    required: false,
    type: String
  },
  closable: {
    required: false,
    type: Boolean
  },
  disabled: {
    required: false,
    type: Boolean
  },
  href: {
    default: undefined,
    required: false,
    type: String
  },
  icon: {
    default: undefined,
    required: false,
    type: String
  },
  id: {
    required: true,
    type: String
  },
  label: {
    default: '',
    required: false,
    type: String
  },
  name: {
    default: '',
    required: false,
    type: String
  },
  onClickClose: {
    default: () => {},
    required: false,
    type: Function
  }
})
</script>

<style lang="scss">
.pill-item {
  background-color: rgba(var(--v-theme-surface));
  border-color: color-mix(in srgb, currentColor 60%, transparent) !important;
  border-style: solid !important;
  border-width: 1px !important;
  display: flex;
  font-size: 0.875rem;
  font-weight: bold;
  padding: 3px 12px;
}
</style>
