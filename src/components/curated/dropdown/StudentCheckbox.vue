<template>
  <div class="student-checkbox">
    <b-form-checkbox
      :id="`student-${student.sid}-curated-group-checkbox`"
      v-model="status"
      :aria-label="checkboxDescription"
      size="sm"
      @change="toggle"
    />
  </div>
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'StudentCheckbox',
  mixins: [Context],
  props: {
    student: Object
  },
  data: () => ({
    status: false
  }),
  computed: {
    checkboxDescription() {
      const name = `${this.student.firstName} ${this.student.lastName}`
      return this.checked
        ? `${name} selected, ready to add to curated group`
        : `Select ${name} to add to curated group`
    }
  },
  created() {
    this.$eventHub.on('curated-group-select-all', () => (this.status = true))
    this.$eventHub.on('curated-group-deselect-all', () => (this.status = false))
  },
  methods: {
    toggle(checked) {
      this.$eventHub.emit(checked ? 'curated-group-checkbox-checked' : 'curated-group-checkbox-unchecked', this.student.sid)
      this.alertScreenReader(`${this.student.name} ${checked ? 'selected' : 'deselected'}`)
    }
  }
}
</script>

<style scoped>
.student-checkbox {
  background-color: #eee;
  border: 1px solid #aaa;
  border-radius: 6px;
  height: 24px;
  padding-left: 4px;
  width: 24px;
}
</style>
