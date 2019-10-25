<template>
  <b-form-checkbox
    :id="`student-${student.sid}-curated-group-checkbox`"
    v-model="status"
    @change="toggle"
    plain>
    <span class="sr-only">{{ checkboxDescription }}</span>
  </b-form-checkbox>
</template>

<script>
export default {
  name: 'CuratedStudentCheckbox',
  props: {
    student: Object
  },
  data: () => ({
    status: false
  }),
  computed: {
    checkboxDescription() {
      const name = `${this.student.firstName} ${this.student.lastName}`;
      return this.checked
        ? `${name} selected, ready to add to curated group`
        : `Select ${name} to add to curated group`;
    }
  },
  created() {
    this.$eventHub.$on('curated-group-select-all', () => (this.status = true));
    this.$eventHub.$on(
      'curated-group-deselect-all',
      () => (this.status = false)
    );
  },
  methods: {
    toggle(checked) {
      this.$eventHub.$emit(
        checked
          ? 'curated-group-checkbox-checked'
          : 'curated-group-checkbox-unchecked',
        this.student.sid
      );
    }
  }
};
</script>
