<template>
  <div
    id="appointment-student-input"
    :class="{'demo-mode-blur': $currentUser.inDemoMode}"
    class="d-flex pill pill-student text-uppercase text-nowrap">
    <div class="student-label">
      <span class="sr-only">Student: </span> {{ student.label }}
    </div>
    <div class="mb-1 mr-2">
      <b-btn
        id="appointment-student-remove"
        variant="link"
        class="p-0"
        @click.prevent="removeStudent">
        <font-awesome icon="times-circle" class="font-size-24 faint-text pl-2" />
      </b-btn>
      <label class="sr-only" for="appointment-student-remove">
        Remove student
      </label>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AppointmentStudentPill',
  props: {
    removeStudent: {
      type: Function,
      required: true
    },
    student: {
      type: Object,
      required: true
    }
  }
};
</script>

<style scoped>
.pill-student {
  height: 32px;
}
.student-label {
  font-size: 14px;
  margin: 2px 4px 0 8px;
}
</style>
