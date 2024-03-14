<template>
  <div>
    <v-expansion-panels v-model="showWarning" class="p-3 mt-2 mb-3 warning">
      <v-expansion-panel>
        <span v-if="warning">{{ warning }}</span>
        <ul v-if="sidsNotFound.length && (sidsNotFound.length <= magicNumber)" id="sids-not-found" class="mb-0 mt-1">
          <li v-for="sid in sidsNotFound" :key="sid">{{ sid }}</li>
        </ul>
      </v-expansion-panel>
    </v-expansion-panels>
    <label
      for="create-note-add-student-input"
      class="font-size-14 font-weight-bold"
    >
      Student
    </label>
    <div id="create-note-add-student-desc" class="font-size-14 pb-2">
      Type a name, individual Student Identification (SID), or paste a list of SID numbers below. (Example: 9999999990, 9999999991)
    </div>
    <div class="pb-2">
      <Autocomplete
        id="create-note-add-student"
        :key="resetAutoCompleteKey"
        aria-describedby="create-note-add-student-desc"
        class="w-75"
        :disabled="disabled"
        :fallback="handleListInput"
        :fallback-when="isList"
        :fetch="studentsByNameOrSid"
        input-labelled-by="create-note-add-student-label"
        option-label-key="name"
        option-value-key="sid"
        maxlength="-1"
        :on-esc="onEscFormInput"
        :suggest-when="isSuggestible"
        :on-click-add-button="addStudent"
      />
    </div>
    <div v-for="(addedStudent, index) in addedStudents" :key="addedStudent.sid" class="pb-1">
      <v-chip
        :id="`batch-note-student-${index}`"
        class="v-chip-content-override font-weight-bold text-medium-emphasis text-uppercase text-nowrap truncate-with-ellipsis"
        :class="{'demo-mode-blur': useContextStore().currentUser.inDemoMode}"
        closable
        :close-label="`Remove ${addedStudent.label} from batch note`"
        density="comfortable"
        variant="outlined"
        @click:close="remove(addedStudent)"
        @keyup.enter="remove(addedStudent)"
      >
        <span class="truncate-with-ellipsis">{{ addedStudent.label }}</span>
        <template #close>
          <v-icon color="error" :icon="mdiCloseCircle"></v-icon>
        </template>
      </v-chip>
    </div>
  </div>
</template>

<script setup>
import {mdiCloseCircle} from '@mdi/js'
</script>

<script>
import Autocomplete from '@/components/util/Autocomplete'
import {each, filter, findIndex, includes, map, remove, split, trim, uniq, without} from 'lodash'
import {findStudentsByNameOrSid, getStudentsBySids} from '@/api/student'
import {putFocusNextTick} from '@/lib/utils'
import {setNoteRecipient, setNoteRecipients} from '@/stores/note-edit-session/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

export default {
  name: 'BatchNoteAddStudent',
  components: {
    Autocomplete
  },
  props: {
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
  computed: {
    disabled() {
      return useNoteStore().isSaving || useNoteStore().boaSessionExpired
    }
  },
  mounted() {
    if (useNoteStore().recipients.sids.length) {
      getStudentsBySids(useNoteStore().recipients.sids).then(students => {
        each(students, student => {
          this.addStudent(student)
        })
      })
    }
  },
  methods: {
    addStudent(student) {
      if (student && !useNoteStore().recipients.sids.includes(student.sid)) {
        useNoteStore().setIsRecalculating(true)
        this.addedStudents.push(student)
        setNoteRecipient(student.sid).then(() => {
          this.resetAutoCompleteKey = new Date().getTime()
          useContextStore().alertScreenReader(`${student.label} added to batch note`)
          this.clearWarning()
        })
      }
    },
    clearWarning() {
      this.warning = null
      this.showWarning = false
    },
    handleListInput(query) {
      const trimmed = trim(query, ' ,\n\t')
      if (trimmed) {
        const sids = split(query, this.sidDelimiter)
        return getStudentsBySids(sids).then(data => {
          useNoteStore().setIsRecalculating(true)
          const sidList = []
          each(data, student => {
            this.addedStudents.push(student)
            sidList.push(student.sid)
            remove(sids, s => s === student.sid)
          })
          setNoteRecipients(
            useNoteStore().recipients.cohorts,
            useNoteStore().recipients.curatedGroups,
            uniq(useNoteStore().recipients.sids.concat(sidList))
          ).then(() => {
            useContextStore().alertScreenReader(`${sidList.length} students added to batch note`)
            this.sidsNotFound = uniq(sids)
            if (this.sidsNotFound.length) {
              this.setWarning(this.sidsNotFound.length === 1 ? 'One student ID not found.' : `${this.sidsNotFound.length} student IDs not found.`)
            } else {
              this.clearWarning()
            }
            putFocusNextTick('create-note-add-student-input')
          })
        })
      } else {
        return Promise.resolve()
      }
    },
    isList(query) {
      return query && this.sidDelimiter.test(trim(query, ' ,\n\t'))
    },
    isPresent(query) {
      return query && query.length > 1
    },
    isSuggestible(query) {
      return this.isPresent(query) && !this.isList(query)
    },
    remove(student) {
      if (student) {
        const index = findIndex(this.addedStudents, {'sid': student.sid})
        this.addedStudents.splice(index, 1)
        if (useNoteStore().recipients.sids.includes(student.sid)) {
          setNoteRecipients(
            useNoteStore().recipients.cohorts,
            useNoteStore().recipients.curatedGroups,
            without(useNoteStore().recipients.sids, student.sid)
          ).then(() => {
            putFocusNextTick('create-note-add-student-input')
          })
        }
        useContextStore().alertScreenReader(`${student.label} removed from batch note`)
      }
    },
    setWarning(message) {
      this.warning = message
      this.showWarning = true
      useContextStore().alertScreenReader(message)
    },
    studentsByNameOrSid(query, limit) {
      const sids = map(this.addedStudents, 'sid')
      return new Promise(resolve => {
        findStudentsByNameOrSid(query, limit).then(students => {
          resolve(filter(students, s => !includes(sids, s.sid)))
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

