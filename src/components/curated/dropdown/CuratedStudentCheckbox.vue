<template>
  <div class="checkbox-container" :class="{'checked-checkbox-container': status}">
    <input
      :id="checkboxId"
      v-model="status"
      :aria-label="ariaLabel"
      class="checkbox"
      type="checkbox"
      @update:model-value="toggle"
    />
  </div>
</template>

<script>
import {alertScreenReader} from '@/lib/utils'
import {describeCuratedGroupDomain} from '@/berkeley'
import {useContextStore} from '@/stores/context'

export default {
  name: 'CuratedStudentCheckbox',
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
    useContextStore().setEventHandler('curated-group-select-all', this.onSelectAll)
    useContextStore().setEventHandler('curated-group-deselect-all', this.onDeselectAll)
  },
  unmounted() {
    useContextStore().removeEventHandler('curated-group-select-all', this.onSelectAll)
    useContextStore().removeEventHandler('curated-group-deselect-all', this.onDeselectAll)
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
      useContextStore().broadcast(eventName, {domain: this.domain, sid: this.sid})
      alertScreenReader(`${this.studentName} ${checked ? 'selected' : 'deselected'}`)
    }
  }
}
</script>

<style scoped>
.checkbox {
  accent-color: #3b7ea5;
  height: 18px;
  width: 18px;
}
.checked-checkbox-container {
  background-color: #96C3de !important;
}
.checkbox-container {
  background-color: #eee;
  border: 1px solid #666;
  border-radius: 6px;
  height: 28px;
  margin-right: 8px;
  padding-top: 5px;
  text-align: center;
  width: 28px;
}
</style>
