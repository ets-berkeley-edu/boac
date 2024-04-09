<template>
  <div class="mb-2">
    <div class="font-weight-bold">
      <span v-if="!plan.degreeProgramUrl" class="no-wrap">{{ plan.description }}</span>
      <a
        v-if="plan.degreeProgramUrl"
        :href="plan.degreeProgramUrl"
        :aria-label="`Open ${plan.description} program page in new window`"
        target="_blank"
      >
        {{ plan.description }}</a>
    </div>
    <div v-if="plan.program" class="text-muted">
      {{ plan.program }}
    </div>
    <div v-if="!active" class="font-weight-bold has-error small text-uppercase">
      {{ plan.status }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentProfilePlan',
  props: {
    active: {
      required: true,
      type: Boolean
    },
    plan: {
      required: true,
      type: Object
    }
  }
}
</script>
