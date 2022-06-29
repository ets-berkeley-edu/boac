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
      <Autocomplete
        id="create-note-add-student"
        :key="resetAutoCompleteKey"
        class="w-75"
        :demo-mode-blur="true"
        :disabled="disabled"
        :fallback="handleListInput"
        :fallback-when="isList"
        input-labelled-by="create-note-add-student-label"
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
            @click.prevent="removeStudent(addedStudent)"
          >
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
import {findStudentsByNameOrSid, getStudentsBySids} from '@/api/student'

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
    addSidList: {
      required: true,
      type: Function
    },
    disabled: {
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
    magicNumber: 15,
    resetAutoCompleteKey: undefined,
    showWarning: false,
    sidDelimiter: /[,\r\n\t ]+/,
    sidsNotFound: [],
    warning: undefined
  }),
  methods: {
    addStudent(student) {
      if (student) {
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
      const trimmed = this.$_.trim(query, ' ,\n\t')
      if (trimmed) {
        const sids = this.$_.split(query, this.sidDelimiter)
        return getStudentsBySids(sids).then(data => {
          const sidList = []
          this.$_.each(data, student => {
            this.addedStudents.push(student)
            sidList.push(student.sid)
            this.$_.remove(sids, s => s === student.sid)
          })
          this.addSidList(sidList)
          this.$announcer.polite(`${sidList.length} students added to batch note`)
          this.sidsNotFound = this.$_.uniq(sids)
          if (this.sidsNotFound.length) {
            this.setWarning(this.sidsNotFound.length === 1 ? 'One student ID not found.' : `${this.sidsNotFound.length} student IDs not found.`)
          } else {
            this.clearWarning()
          }
        })
      } else {
        return Promise.resolve()
      }
    },
    isList(query) {
      return query && this.sidDelimiter.test(this.$_.trim(query, ' ,\n\t'))
    },
    isPresent(query) {
      return query && query.length > 1
    },
    isSuggestible(query) {
      return this.isPresent(query) && !this.isList(query)
    },
    removeStudent(student) {
      if (student) {
        this.addedStudents = this.$_.filter(this.addedStudents, a => a.sid !== student.sid)
        this.removeSid(student.sid)
        this.$announcer.polite(`${student.label} removed from batch note`)
      }
    },
    setWarning(message) {
      this.warning = message
      this.showWarning = true
      this.$announcer.polite(message)
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

<style scoped>
.warning {
  background-color: #fbf7dc;
  border-radius: 5px;
  color: #795f31;
}
</style>

