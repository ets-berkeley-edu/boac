<template>
  <v-badge
    :id="`timeline-category-${message.type}-${message.id}`"
    :aria-atomic="undefined"
    :aria-label="undefined"
    :aria-live="undefined"
    bordered
    class="v-badge-override timeline-category"
    :class="`timeline-category-${getCategoryType(message)}`"
    :color="getCategoryColor(message)"
    height="1.5rem"
    inline
    role="none"
    rounded="sm"
  >
    <template #badge>
      <span class="font-weight-bold font-size-12 text-uppercase">{{ message.type === 'note' && message.peerAdvisingDepartmentId ? 'Peer Note' : label }}</span>
    </template>
  </v-badge>
</template>

<script setup>
defineProps({
  label: {
    required: true,
    type: String
  },
  message: {
    required: true,
    type: Object
  }
})

const getCategoryColor = message => `category-${message.type === 'note' && message.peerAdvisingDepartmentId ? 'peer-note' : message.type}`

const getCategoryType = message => {
  return message.type === 'note' && message.peerAdvisingDepartmentId ? 'peer-advising' : message.type
}
</script>

<style>
.timeline-category {
  margin-top: 8px;
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
