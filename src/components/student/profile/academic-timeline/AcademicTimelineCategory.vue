<template>
  <v-badge
    :id="`${idPrefix}-${messageType}-${message.id}`"
    :aria-atomic="undefined"
    :aria-label="undefined"
    :aria-live="undefined"
    bordered
    class="v-badge-override timeline-category"
    :class="`timeline-category-${categoryType}`"
    :color="categoryColor"
    height="1.5rem"
    inline
    role="none"
    rounded="sm"
  >
    <template #badge>
      <span :aria-hidden="true" class="font-weight-bold font-size-12 text-uppercase">
        {{ label }}
      </span>
      <span class="sr-only">{{ label }}</span>
    </template>
  </v-badge>
</template>

<script setup>
import {computed} from 'vue'

const props = defineProps({
  idPrefix: {
    default: 'timeline-category',
    required: false,
    type: String
  },
  label: {
    required: true,
    type: String
  },
  message: {
    required: true,
    type: Object
  }
})

const categoryColor = computed(() => `category-${messageType.value === 'note' && props.message.peerAdvisingDepartmentId ? 'peer-note' : messageType}`)
const categoryType = computed(() => messageType === 'note' && props.message.peerAdvisingDepartmentId ? 'peer-advising' : messageType)
const messageType = props.message.type || props.message.objectType
</script>

<style>
.timeline-category {
  margin: 8px 0;
  .v-badge__badge {
    border-radius: 4px !important;
  }
  .v-badge__badge::after {
    border-color: rgba(var(--v-theme-on-surface), var(--v-border-opacity)) !important;
    transform: unset;
    vertical-align: middle;
  }
}
/* eslint-disable vue-scoped-css/no-unused-selector */
.timeline-category-alert .v-badge__badge {
  width: 3.75rem;
}
.timeline-category-appointment .v-badge__badge {
  width: 7.5rem;
}
.timeline-category-eForm .v-badge__badge {
  width: 4.5rem;
}
.timeline-category-hold .v-badge__badge {
  width: 3.75rem;
}
.timeline-category-note .v-badge__badge {
  width: 7.5rem;
}
.timeline-category-peer-advising .v-badge__badge {
  width: 6rem;
}
.timeline-category-requirement .v-badge__badge {
  width: 7.25rem;
}
/* eslint-enable vue-scoped-css/no-unused-selector */
</style>
