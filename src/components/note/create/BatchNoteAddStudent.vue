<template>
  <div>
    <div>
      <label
        for="create-note-add-student"
        class="font-size-14 input-label text mt-2">
        <span class="sr-only">Add a </span><span class="font-weight-bolder">Student</span> (name or SID)
        <span class="sr-only">(expect auto-suggest based on what you enter)</span>
      </label>
    </div>
    <div class="mb-2">
      <Autocomplete
        id="create-note-add-student"
        :key="resetAutoCompleteKey"
        :disabled="disabled"
        :demo-mode-blur="true"
        :on-esc-form-input="onEscFormInput"
        :show-add-button="true"
        :source="studentsByNameOrSid"
        class="w-75"
        @input="addStudent">
      </Autocomplete>
    </div>
    <div>
      <div v-for="(addedStudent, index) in addedStudents" :key="addedStudent.sid" class="mb-1">
        <span class="font-weight-bolder pill pill-attachment text-uppercase text-nowrap truncate">
          <span :id="`batch-note-student-${index}`" :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ addedStudent.label }}</span>
          <b-btn
            :id="`remove-student-from-batch-${index}`"
            variant="link"
            class="p-0"
            @click.prevent="removeStudent(addedStudent)">
            <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
            <span class="sr-only">Remove {{ addedStudent.label }} from batch note</span>
          </b-btn>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import Autocomplete from '@/components/util/Autocomplete'
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import { findStudentsByNameOrSid } from '@/api/student'

export default {
  name: 'BatchNoteAddStudent',
  components: {
    Autocomplete
  },
  mixins: [Context, Util],
  props: {
    addSid: {
      required: true,
      type: Function
    },
    disabled: {
      default: false,
      required: false,
      type: Boolean
    },
    onEscFormInput: {
      default: () => {},
      required: false,
      type: Function
    },
    removeSid: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    addedStudents: [],
    resetAutoCompleteKey: undefined
  }),
  methods: {
    addStudent(student) {
      if (student) {
        this.addedStudents.push(student)
        this.addSid(student.sid)
        this.resetAutoCompleteKey = new Date().getTime()
        this.alertScreenReader(`${student.label} added to batch note`)
      }
    },
    removeStudent(student) {
      if (student) {
        this.addedStudents = this.filterList(this.addedStudents, a => a.sid !== student.sid)
        this.removeSid(student.sid)
        this.alertScreenReader(`${student.label} removed from batch note`)
      }
    },
    studentsByNameOrSid(query, limit) {
      const sids = this.map(this.addedStudents, 'sid')
      return new Promise(resolve => {
        findStudentsByNameOrSid(query, limit).then(students => {
          resolve(this.filterList(students, s => !this.includes(sids, s.sid)))
        })
      })
    }
  }
}
</script>
