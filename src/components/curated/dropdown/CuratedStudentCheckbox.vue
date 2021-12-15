<template>
  <div class="student-checkbox">
    <b-form-checkbox
      :id="checkboxId"
      v-model="status"
      :aria-label="ariaLabel"
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
    checkboxId: undefined,
    sid: undefined,
    status: false,
    studentName: undefined
  }),
  computed: {
    ariaLabel() {
      const domainLabel = this.describeCuratedGroupDomain(this.domain, true)
      return this.status ? `${this.studentName} selected, ready to add to ${domainLabel}` : `Select ${this.studentName} to add to ${domainLabel}`
    }
  },
  created() {
    const idFragment = this.describeCuratedGroupDomain(this.domain, false).replace(' ', '-')
    this.sid = this.student.sid || this.student.csEmplId
    this.checkboxId = `${this.domain === 'admitted_students' ? 'admit' : 'student'}-${this.sid}-${idFragment}-checkbox`
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
