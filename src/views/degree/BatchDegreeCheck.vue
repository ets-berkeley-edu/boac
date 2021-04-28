<template>
  <div v-if="!loading" class="ml-3 mr-3 mt-3">
    <h1 class="page-section-header">Batch Degree Checks</h1>
    <div>
      <label
        for="degree-check-add-student-input"
        class="font-size-14 input-label text mt-2"
      >
        <span class="font-weight-bolder">Student</span>
        <span>Type a name, individual Student Identification (SID), or paste a list of SID numbers below. Example: 9999999990, 9999999991</span>
      </label>
    </div>
    <div class="mb-2">
      <span id="degree-check-add-student-label" class="sr-only">Select student for degree check. Expect auto-suggest as you type name or SID.</span>
      <Autocomplete
        id="degree-check-add-student"
        :key="resetAutoCompleteKey"
        class="w-75"
        :demo-mode-blur="true"
        :disabled="disabled"
        input-labelled-by="degree-check-add-student-label"
        :show-add-button="true"
        :source="studentsByNameOrSid"
        @input="addStudent"
      />
    </div>
    <div>
      <div v-for="(addedStudent, index) in addedStudents" :key="addedStudent.sid" class="mb-1">
        <span class="font-weight-bolder pill pill-attachment text-uppercase text-nowrap truncate">
          <span :id="`batch-note-student-${index}`" :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ addedStudent.label }}</span>
          <b-btn
            :id="`remove-student-from-batch-${index}`"
            variant="link"
            class="p-0"
            @click.prevent="removeStudent(addedStudent)"
          >
            <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
            <span class="sr-only">Remove {{ addedStudent.label }} from degree check</span>
          </b-btn>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import Autocomplete from '@/components/util/Autocomplete'
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading'
import Util from '@/mixins/Util'
import {findStudentsByNameOrSid} from '@/api/student'

export default {
  name: 'BatchDegreeCheck',
  components: {
    Autocomplete
  },
  mixins: [Context, Loading, Util],
  data: () => ({
    addedStudents: [],
    disabled: false,
    isRecalculating: false,
    resetAutoCompleteKey: undefined,
  }),
  computed: {
    sids() {
      return this.$_.map(this.addedStudents, 'sid')
    }
  },
  mounted() {
    this.loaded('Batch degree checks')
  },
  methods: {
    addStudent(student) {
      if (student) {
        this.addedStudents.push(student)
        this.resetAutoCompleteKey = new Date().getTime()
        this.alertScreenReader(`${student.label} added to degree check`)
      }
      this.putFocusNextTick('degree-check-add-student-input')
    },
    removeStudent(student) {
      if (student) {
        this.addedStudents = this.$_.filter(this.addedStudents, a => a.sid !== student.sid)
        this.alertScreenReader(`${student.label} removed from degree check`)
      }
    },
    studentsByNameOrSid(query, limit) {
      const sids = this.$_.map(this.addedStudents, 'sid')
      return new Promise(resolve => {
        findStudentsByNameOrSid(query, limit).then(students => {
          resolve(this.$_.filter(students, s => !this.$_.includes(sids, s.sid)))
        })
      })
    }
  }
}
</script>
