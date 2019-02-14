<template>
  <b-form-checkbox
    :id="`student-${sid}-curated-group-checkbox`"
    v-model="status"
    plain
    @change="toggle">
    <span class="sr-only">{{ checkboxDescription }}</span>
  </b-form-checkbox>
</template>

<script>
export default {
  name: 'CuratedStudentCheckbox',
  props: {
    sid: String
  },
  data: () => ({
    status: false
  }),
  computed: {
    checkboxDescription() {
      return this.checked
        ? `Student ${this.sid} selected, ready to add to curated group`
        : `Select student ${this.sid} to add to curated group`;
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
        this.sid
      );
    }
  }
};
</script>
