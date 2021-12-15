<template>
  <div class="student-checkbox">
    <b-form-checkbox
      :id="`${domain === 'admitted_students' ? 'admit' : 'student'}-${sid}-curated-group-checkbox`"
      v-model="status"
      :aria-label="status ? `${studentName} selected, ready to add to ${domainLabel}` : `Select ${studentName} to add to ${domainLabel}`"
      size="sm"
      @change="toggle"
    />
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'

export default {
  name: 'CuratedStudentCheckbox',
  mixins: [Context, Util],
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
    status: false,
    studentName: undefined
  }),
  created() {
    this.sid = this.student.sid || this.student.csEmplId
    this.studentName = `${this.student.firstName} ${this.student.lastName}`
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
    domainLabel(capitalize) {
      return this.describeCuratedGroupDomain(this.domain, capitalize)
    },
    toggle(checked) {
      const eventName = checked ? 'curated-group-checkbox-checked' : 'curated-group-checkbox-unchecked'
      this.$eventHub.emit(eventName, {domain: this.domain, sid: this.sid})
      this.$announcer.polite(`${this.studentName} ${checked ? 'selected' : 'deselected'}`)
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
