<template>
  <span>
    <strong v-if="alert.alertType === 'late_assignment'">Late assignment!</strong>
    <strong v-if="alert.alertType === 'missing_assignment'">Missed assignment!</strong>
    {{ alert.message }}
  </span>
</template>

<script>
export default {
  name: 'StudentAlertMessage',
  props: {
    alert: Object
  }
};
</script>
