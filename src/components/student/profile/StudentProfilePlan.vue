<template>
  <div class="mb-2">
    <div class="font-weight-bold">
      <span v-if="!plan.degreeProgramUrl" class="text-no-wrap">{{ plan.description }}</span>
      <a
        v-if="plan.degreeProgramUrl"
        :href="plan.degreeProgramUrl"
        :aria-label="`${plan.description} program page (opens in new window)`"
        target="_blank"
      >
        {{ plan.description }}</a>
    </div>
    <div v-if="plan.program" class="text-medium-emphasis">
      {{ plan.program }}
    </div>
    <div v-if="!active" class="font-weight-bold text-errorr small text-uppercase">
      {{ plan.status }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  active: {
    required: true,
    type: Boolean
  },
  plan: {
    required: true,
    type: Object
  }
})
</script>
