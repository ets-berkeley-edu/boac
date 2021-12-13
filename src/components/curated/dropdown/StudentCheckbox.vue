<template>
  <div class="student-checkbox">
    <b-form-checkbox
      :id="`student-${sid}-curated-group-checkbox`"
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
    domain: {
      required: true,
      type: String
    },
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    sid: undefined,
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
    this.sid = this.domain === 'default' ? this.student.sid : this.student.csEmplId
    this.$eventHub.on('curated-group-select-all', domain => {
      if (this.domain === domain) {
        this.status = true
      }
    })
    this.$eventHub.on('curated-group-deselect-all', domain => {
      if (this.domain === domain) {
        this.status = false
      }
    })
  },
  methods: {
    toggle(checked) {
      const eventName = checked ? 'curated-group-checkbox-checked' : 'curated-group-checkbox-unchecked'
      this.$eventHub.emit(eventName, {domain: this.domain, sid: this.sid})
      this.$announcer.polite(`${this.student.name} ${checked ? 'selected' : 'deselected'}`)
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
  padding-top: 1px;
  width: 24px;
}
</style>
