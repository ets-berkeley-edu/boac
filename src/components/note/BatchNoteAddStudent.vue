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
      Type a name, individual Student Identification (SID), or paste a list of SID numbers below.
      (Example: 9999999990, 9999999991)
    </div>
    <div class="align-center d-flex pb-2 w-75">
      <v-autocomplete
        id="create-note-add-student"
        :key="key"
        aria-describedby="create-note-add-student-desc"
        auto-select-first
        class="autocomplete-students autocomplete-with-add-button"
        :class="{'demo-mode-blur': useContextStore().currentUser.inDemoMode}"
        density="comfortable"
        :disabled="disabled"
        hide-details
        :hide-no-data="size(autoSuggestedStudents) < 3"
        item-title="label"
        item-value="sid"
        :items="autoSuggestedStudents"
        :menu-icon="null"
        variant="outlined"
        @click:clear="resetAutocomplete"
        @update:search="onChangeAutocompleteQuery"
        @update:modelValue="onSelectSuggestedStudent"
        @keydown.esc="onEscFormInput"
      >
        <template #append="{}">
          <v-btn
            id="create-note-add-student-add-button"
            class="add-button"
            color="primary"
            :disabled="!size(sidsManuallyAdded) || isUpdatingStudentAutocomplete"
            variant="flat"
            @click="onClickAddButton"
          >
            <v-icon :icon="mdiPlus" /> Add
          </v-btn>
        </template>
      </v-autocomplete>
    </div>
    <div v-for="(addedStudent, index) in addedStudents" :key="addedStudent.sid" class="pb-1">
      <v-chip
        :id="`batch-note-student-${index}`"
        class="v-chip-content-override font-weight-bold text-medium-emphasis text-uppercase text-no-wrap truncate-with-ellipsis"
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
import {mdiCloseCircle, mdiPlus} from '@mdi/js'
</script>

<script>
import {each, filter, find, findIndex, includes, map, remove, size, split, trim, uniq, without} from 'lodash'
import {findStudentsByNameOrSid, getStudentsBySids} from '@/api/student'
import {putFocusNextTick} from '@/lib/utils'
import {setNoteRecipient, setNoteRecipients} from '@/stores/note-edit-session/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

export default {
  name: 'BatchNoteAddStudent',
  props: {
    onEscFormInput: {
      default: () => {},
      required: false,
      type: Function
    }
  },
  data: () => ({
    addedStudents: [],
    autocompleteModel: undefined,
    autoSuggestedStudents: [],
    isUpdatingStudentAutocomplete: false,
    key: new Date(),
    magicNumber: 15,
    showWarning: false,
    sidsManuallyAdded: [],
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
          this.onSelectSuggestedStudent(student.sid)
        })
      })
    }
  },
  methods: {
    clearWarning() {
      this.warning = null
      this.showWarning = false
    },
    extractDelimitedSids(query) {
      return /^[0-9,\s]*$/.test(query) ? uniq(split(query, /\s+|,+,/)) : []
    },
    onChangeAutocompleteQuery(query) {
      query = this.trimAndScrubQueryInput(query)
      this.isUpdatingStudentAutocomplete = true
      if (size(query) > 1) {
        this.sidsManuallyAdded = this.extractDelimitedSids(query)
        findStudentsByNameOrSid(query, 20).then(students => {
          const existingSids = map(this.addedStudents, 'sid')
          students = filter(students, s => !includes(existingSids, s.sid))
          this.autoSuggestedStudents = map(students, s => ({label: s.label, sid: s.sid}))
        })
      }
    },
    onClickAddButton() {
      if (this.sidsManuallyAdded) {
        return getStudentsBySids(this.sidsManuallyAdded).then(data => {
          useNoteStore().setIsRecalculating(true)
          const sidList = []
          each(data, student => {
            this.addedStudents.push(student)
            sidList.push(student.sid)
            remove(this.sidsManuallyAdded, s => s === student.sid)
          })
          setNoteRecipients(
            useNoteStore().recipients.cohorts,
            useNoteStore().recipients.curatedGroups,
            uniq(useNoteStore().recipients.sids.concat(sidList))
          ).then(() => {
            useContextStore().alertScreenReader(`${sidList.length} students added to batch note`)
            this.sidsNotFound = uniq(this.sidsManuallyAdded)
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
    onSelectSuggestedStudent(sid) {
      this.clearWarning()
      const student = sid ? find(this.autoSuggestedStudents, ['sid', sid]) : null
      if (student && !useNoteStore().recipients.sids.includes(student.sid)) {
        useNoteStore().setIsRecalculating(true)
        this.addedStudents.push(student)
        setNoteRecipient(sid).then(() => {
          useContextStore().alertScreenReader(`${student.label} added to batch note`)
          this.resetAutocomplete()
        })
      } else {
        this.resetAutocomplete()
      }
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
    resetAutocomplete() {
      this.autoSuggestedStudents = []
      this.isUpdatingStudentAutocomplete = false
      this.key = new Date()
      this.sidsManuallyAdded = []
    },
    setWarning(message) {
      this.warning = message
      this.showWarning = true
      useContextStore().alertScreenReader(message)
    },
    trimAndScrubQueryInput(query) {
      return trim(query, ' ,\n\t').replace((/\s+|\r\n|\n|\r/gm),' ')
    }
  }
}
</script>

<style scoped>
autocomplete-students {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
}
.add-button {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
  height: 40px !important;
}
.warning {
  background-color: #fbf7dc;
  border-radius: 5px;
  color: #795f31;
}
</style>

