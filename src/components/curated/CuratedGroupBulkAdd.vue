<template>
  <div>
    <div class="mt-3 w-100">
      <v-alert
        v-if="showWarning"
        id="curated-group-bulk-add-alert"
        aria-live="polite"
        class="v-alert-override w-100 mb-5"
        density="compact"
        type="warning"
        variant="tonal"
      >
        <v-alert-title class="font-size-16 text-warning-darken-1">
          <div v-if="warning" class="mr-2">{{ warning }}</div>
          <div v-if="sids.length && sidsNotFound.length">{{ sidsNotFound.length === 1 ? 'Remove from list?' : 'Remove these from your list?' }}</div>
          <div v-if="!sids.length || sidsNotFound.length" class="ml-2" :class="{'ms-auto': !sids.length}">
            <v-btn
              id="remove-invalid-sids-btn"
              :aria-label="sids.length ? 'Remove invalid SIDs' : 'Clear the textarea'"
              class="font-size-16"
              color="primary-darken-1"
              :text="sids.length ? 'Yes' : 'Clear the textarea'"
              variant="text"
              @click="scrub"
            />
          </div>
        </v-alert-title>
        <ul v-if="sids.length && sidsNotFound.length && (sidsNotFound.length <= magicNumber)" id="sids-not-found" class="mb-1 pl-6">
          <li v-for="sid in sidsNotFound" :key="sid">{{ sid }}</li>
        </ul>
      </v-alert>
      <div>
        <v-textarea
          id="curated-group-bulk-add-sids"
          v-model="textarea"
          aria-describedby="page-description"
          aria-labelledby="page-section-header"
          :disabled="isValidating || isSaving"
          label="Enter SIDs here"
          variant="outlined"
        />
      </div>
      <div class="d-flex float-right">
        <ProgressButton
          id="btn-curated-group-bulk-add-sids"
          :action="submit"
          :disabled="!trim(textarea) || isValidating || isSaving"
          :in-progress="isValidating || isSaving"
          :text="isValidating || isSaving ? 'Adding' : (curatedGroupId ? 'Add' : 'Next')"
        />
        <v-btn
          v-if="curatedGroupId"
          id="btn-cancel-bulk-add-sids"
          class="ml-2"
          color="primary"
          :disabled="isValidating || isSaving"
          text="Cancel"
          variant="text"
          @click="cancel"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton.vue'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {each, partition, split, trim, uniq} from 'lodash'
import {onMounted, ref} from 'vue'
import {validateSids} from '@/api/student'

const props = defineProps({
  bulkAddSids: {
    required: true,
    type: Function
  },
  curatedGroupId: {
    default: undefined,
    required: false,
    type: Number
  },
  domain: {
    default: undefined,
    required: false,
    type: String
  },
  isSaving: {
    required: false,
    type: Boolean
  }
})

const isValidating = ref(false)
const magicNumber = ref(15)
const showWarning = ref(false)
const sids = ref([])
const sidsNotFound = ref([])
const textarea = ref(undefined)
const warning = ref(undefined)

onMounted(() => {
  putFocusNextTick('curated-group-bulk-add-sids')
})

const cancel = () => {
  if (props.curatedGroupId) {
    // Cancel is only supported in the add-students-to-existing-group case.
    clearWarning()
    props.bulkAddSids(null)
    putFocusNextTick('bulk-add-sids-button')
  }
}

const clearWarning = () => {
  showWarning.value = false
  warning.value = undefined
}

const scrub = () => {
  sids.value = uniq(sids.value)
  textarea.value = sids.value.length ? sids.value.join(', ') : ''
  alertScreenReader(`${sidsNotFound.value.length} invalid SIDs removed from textarea.`)
  sidsNotFound.value = []
  clearWarning()
  putFocusNextTick('curated-group-bulk-add-sids')
}

const setWarning = message => {
  warning.value = message
  showWarning.value = true
  alertScreenReader(message)
}

const submit = () => {
  sids.value = []
  sidsNotFound.value = []
  clearWarning()

  const trimmed = trim(textarea.value, ' ,\n\t')
  if (trimmed) {
    const splitted = split(trimmed, /[,\r\n\t ]+/)
    const notNumeric = partition(splitted, sid => /^\d+$/.test(trim(sid)))[1]
    if (notNumeric.length) {
      setWarning('SIDs must be numeric and separated by commas, line breaks, or tabs.')
      putFocusNextTick('curated-group-bulk-add-sids')
    } else {
      isValidating.value = true
      validateSids(props.domain, splitted).then(data => {
        each(data, entry => {
          switch(entry.status) {
          case 200:
          case 401:
            sids.value.push(entry.sid)
            break
          default:
            sidsNotFound.value.push(entry.sid)
          }
        })
        sidsNotFound.value = uniq(sidsNotFound.value)
        isValidating.value = false
        if (sidsNotFound.value.length) {
          const label = props.domain === 'admitted_students' ? 'admit' : 'student'
          if (sids.value.length) {
            setWarning(sidsNotFound.value.length === 1 ? `One ${label} not found.` : `${sidsNotFound.value.length} ${label}s not found.`)
          } else {
            setWarning(`No matching ${label}${sidsNotFound.value.length === 1 ? '' : 's'} found.`)
          }
        } else {
          props.bulkAddSids(uniq(sids.value))
          sids.value = []
        }
      })
    }
  } else {
    setWarning('Please provide one or more SIDs.')
    putFocusNextTick('curated-group-bulk-add-sids')
  }
}
</script>

<style>
.v-alert-override {
  .v-alert__prepend {
    padding-top: 3px;
  }
}</style>
