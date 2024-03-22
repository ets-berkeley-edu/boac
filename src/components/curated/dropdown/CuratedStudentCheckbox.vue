<template>
  <div class="student-checkbox-container">
    <div class="student-checkbox-layer" />
    <div class="student-checkbox-layer">
      <v-checkbox
        :id="checkboxId"
        v-model="status"
        :aria-label="ariaLabel"
        base-color="primary"
        class="student-checkbox"
        color="primary"
        density="compact"
        hide-details
        @update:model-value="toggle"
      />
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {describeCuratedGroupDomain} from '@/berkeley'

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
      const domainLabel = describeCuratedGroupDomain(this.domain, true)
      return this.status ? `${this.studentName} selected, ready to add to ${domainLabel}` : `Select ${this.studentName} to add to ${domainLabel}`
    }
  },
  created() {
    const idFragment = describeCuratedGroupDomain(this.domain, false).replace(' ', '-')
    this.sid = this.student.sid || this.student.csEmplId
    this.checkboxId = `${this.domain === 'admitted_students' ? 'admit' : 'student'}-${this.sid}-${idFragment}-checkbox`
    this.studentName = `${this.student.firstName} ${this.student.lastName}`
    this.setEventHandler('curated-group-select-all', this.onSelectAll)
    this.setEventHandler('curated-group-deselect-all', this.onDeselectAll)
  },
  unmounted() {
    this.removeEventHandler('curated-group-select-all', this.onSelectAll)
    this.removeEventHandler('curated-group-deselect-all', this.onDeselectAll)
  },
  methods: {
    onDeselectAll(domain) {
      if (this.domain === domain) {
        this.status = false
      }
    },
    onSelectAll(domain) {
      if (this.domain === domain) {
        this.status = true
      }
    },
    toggle(checked) {
      const eventName = checked ? 'curated-group-checkbox-checked' : 'curated-group-checkbox-unchecked'
      this.broadcast(eventName, {domain: this.domain, sid: this.sid})
      this.alertScreenReader(`${this.studentName} ${checked ? 'selected' : 'deselected'}`)
    }
  }
}
</script>

<style scoped>
.student-checkbox {
  z-index: 100;
}
.student-checkbox-container {
  background-color: #eee;
  border: 1px solid #aaa;
  border-radius: 36px;
  height: 36px;
  margin-right: 8px;
  position: relative;
  width: 36px;
}
.student-checkbox-layer {
  bottom: 3px;
  height: 100%;
  position: absolute;
  left: 3px;
  width: 100%;
}
</style>
