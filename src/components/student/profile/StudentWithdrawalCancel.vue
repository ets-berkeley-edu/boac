<template>
  <div v-if="withdr && (!termId || withdr.termId === termId)">
    <span class="red-flag-small">
      {{ withdr.description }}
      ({{ withdr.reason }})
      {{ withdr.date | moment('MMM DD, YYYY') }}
    </span>
  </div>
</template>

<script>
  export default {
    name: "StudentWithdrawalCancel",
    props: {
      termId: String,
      withdr: Object
    }
  }
</script>
