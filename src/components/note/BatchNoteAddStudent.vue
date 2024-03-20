<template>
  <div>
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
        :key="vAutocompleteKey"
        aria-describedby="create-note-add-student-desc"
        auto-select-first
        class="autocomplete-students autocomplete-with-add-button"
        :class="{'demo-mode-blur': useContextStore().currentUser.inDemoMode}"
        density="comfortable"
        :disabled="disabled"
        :error-messages="autocompleteErrorMessage"
        :hide-details="!size(autocompleteErrorMessage)"
        :hide-no-data="size(autoSuggestedStudents) < 3"
        item-title="label"
        item-value="sid"
        :items="autoSuggestedStudents"
        :menu-icon="null"
        type="search"
        variant="outlined"
        @click:append="onClickAddButton"
        @click:clear="resetAutocomplete"
        @keydown.esc="onEscFormInput"
        @update:search="onUpdateSearch"
        @update:model-value="onUpdateModel"
      >
        <template #append>
          <v-btn
            id="create-note-add-student-add-button"
            class="add-button"
            color="primary"
            :prepend-icon="mdiPlus"
            text="Add"
            variant="flat"
            @click.stop="onClickAddButton"
          />
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
import {
  differenceWith,
  each,
  filter,
  find,
  findIndex,
  includes, isEqual,
  join,
  map,
  remove,
  size,
  split,
  trim,
  uniq,
  without
} from 'lodash'
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
    autocompleteErrorMessage: undefined,
    autocompleteModel: undefined,
    autoSuggestedStudents: [],
    isUpdatingStudentAutocomplete: false,
    magicNumber: 15,
    query: undefined,
    showWarning: false,
    sidsManuallyAdded: [],
    warning: undefined,
    vAutocompleteKey: new Date()
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
          this.onUpdateModel(student.sid)
        })
      })
    }
  },
  methods: {
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
            const sidsNotFound = differenceWith(this.sidsManuallyAdded, sidList, isEqual)
            console.log(`sidsNotFound: ${sidsNotFound}`)
            if (sidsNotFound.length) {
              const suffix = sidsNotFound.length === 1 ? '' : 's'
              this.autocompleteErrorMessage = `No student${suffix} found with SID${suffix} ${join(sidsNotFound)}.`
            }
            this.resetAutocomplete()
            putFocusNextTick('create-note-add-student-input')
          })
        })
      } else {
        this.resetAutocomplete()
        return Promise.resolve()
      }
    },
    onUpdateModel(sid) {
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
    onUpdateSearch(input) {
      this.autocompleteErrorMessage = undefined
      input = trim(input, ' ,\n\t')
      if (input.length) {
        this.sidsManuallyAdded = /^[0-9,\s]*$/.test(input) ? uniq(split(input, /\s+|,+,/)) : []
        if (!this.sidsManuallyAdded.length) {
          this.query = input.replace((/\s+|\r\n|\n|\r/gm),' ')
          this.isUpdatingStudentAutocomplete = true
          if (size(this.query) > 1) {
            findStudentsByNameOrSid(this.query, 20).then(students => {
              const existingSids = map(this.addedStudents, 'sid')
              students = filter(students, s => !includes(existingSids, s.sid))
              this.autoSuggestedStudents = map(students, s => ({label: s.label, sid: s.sid}))
              this.isUpdatingStudentAutocomplete = false
            })
          }
        }
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
      this.query = undefined
      this.sidsManuallyAdded = []
      this.vAutocompleteKey = new Date()
    }
  }
}
</script>

<style>
.v-input__append:has(button) {
  margin-left: 0 !important;
}
</style>

<style scoped>
autocomplete-students {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
}
.add-button {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
  height: 48px !important;
}
</style>

