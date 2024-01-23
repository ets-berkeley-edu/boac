<template>
  <div>
    <b-collapse v-model="showWarning" class="p-3 mt-2 mb-3 warning">
      <span v-if="warning">{{ warning }}</span>
      <ul v-if="sidsNotFound.length && (sidsNotFound.length <= magicNumber)" id="sids-not-found" class="mb-0 mt-1">
        <li v-for="sid in sidsNotFound" :key="sid">{{ sid }}</li>
      </ul>
    </b-collapse>
    <div>
      <label
        for="create-note-add-student-input"
        class="font-size-14 input-label text mt-2 mb-0"
      >
        <span class="font-weight-bolder">Student</span>
      </label>
      <div class="mb-2">
        Type a name, individual Student Identification (SID), or paste a list of SID numbers below. (Example: 9999999990, 9999999991)
      </div>
    </div>
    <div class="mb-2">
      <InputTextAutocomplete
        id="create-note-add-student"
        :key="resetAutoCompleteKey"
        class="w-75"
        :demo-mode-blur="true"
        :disabled="disabled"
        :fallback="handleListInput"
        :fallback-when="isList"
        input-labelled-by="create-note-add-student-label"
        maxlength="-1"
        :on-esc-form-input="onEscFormInput"
        :show-add-button="true"
        :source="studentsByNameOrSid"
        :suggest-when="isSuggestible"
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
            @click.prevent="remove(addedStudent)"
          >
            <font-awesome icon="times-circle" class="font-size-20 has-error pl-2" />
            <span class="sr-only">Remove {{ addedStudent.label }} from batch note</span>
          </b-btn>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import InputTextAutocomplete from '@/components/util/InputTextAutocomplete'
import NoteEditSession from '@/mixins/NoteEditSession.vue'
import Util from '@/mixins/Util'
import {findStudentsByNameOrSid, getStudentsBySids} from '@/api/student'

export default {
  name: 'BatchNoteAddStudent',
  components: {
    InputTextAutocomplete
  },
  mixins: [Context, NoteEditSession, Util],
  props: {
    disabled: {
      required: false,
      type: Boolean
    },
    onEscFormInput: {
      default: () => {},
      required: false,
      type: Function
    }
  },
  data: () => ({
    addedStudents: [],
    magicNumber: 15,
    resetAutoCompleteKey: undefined,
    showWarning: false,
    sidDelimiter: /[,\r\n\t ]+/,
    sidsNotFound: [],
    warning: undefined
  }),
  mounted() {
    if (this.sids.length) {
      getStudentsBySids(this.sids).then(students => {
        this._each(students, student => {
          this.addStudent(student)
        })
      })
    }
  },
  methods: {
    addStudent(student) {
      if (student) {
        this.setIsRecalculating(true)
        this.addedStudents.push(student)
        this.addSid(student.sid)
        this.resetAutoCompleteKey = new Date().getTime()
        this.$announcer.polite(`${student.label} added to batch note`)
        this.clearWarning()
      }
    },
    clearWarning() {
      this.warning = null
      this.showWarning = false
    },
    handleListInput(query) {
      const trimmed = this._trim(query, ' ,\n\t')
      if (trimmed) {
        const sids = this._split(query, this.sidDelimiter)
        return getStudentsBySids(sids).then(data => {
          this.setIsRecalculating(true)
          const sidList = []
          this._each(data, student => {
            this.addedStudents.push(student)
            sidList.push(student.sid)
            this._remove(sids, s => s === student.sid)
          })
          this.addSidList(sidList)
          this.$announcer.polite(`${sidList.length} students added to batch note`)
          this.sidsNotFound = this._uniq(sids)
          if (this.sidsNotFound.length) {
            this.setWarning(this.sidsNotFound.length === 1 ? 'One student ID not found.' : `${this.sidsNotFound.length} student IDs not found.`)
          } else {
            this.clearWarning()
          }
          this.$putFocusNextTick('create-note-add-student-input')
        })
      } else {
        return Promise.resolve()
      }
    },
    isList(query) {
      return query && this.sidDelimiter.test(this._trim(query, ' ,\n\t'))
    },
    isPresent(query) {
      return query && query.length > 1
    },
    isSuggestible(query) {
      return this.isPresent(query) && !this.isList(query)
    },
    remove(student) {
      if (student) {
        this.addedStudents = this._filter(this.addedStudents, a => a.sid !== student.sid)
        if (this.sids.includes(student.sid)) {
          this.setIsRecalculating(true)
          this.removeStudent(student.sid)
          this.$putFocusNextTick('create-note-add-student-input')
        }
        this.$announcer.polite(`${student.label} removed from batch note`)
      }
    },
    setWarning(message) {
      this.warning = message
      this.showWarning = true
      this.$announcer.polite(message)
    },
    studentsByNameOrSid(query, limit) {
      const sids = this._map(this.addedStudents, 'sid')
      return new Promise(resolve => {
        findStudentsByNameOrSid(query, limit).then(students => {
          resolve(this._filter(students, s => !this._includes(sids, s.sid)))
        })
      })
    }
  }
}
</script>

<style scoped>
.warning {
  background-color: #fbf7dc;
  border-radius: 5px;
  color: #795f31;
}
</style>

