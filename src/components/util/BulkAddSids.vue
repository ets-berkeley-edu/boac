<template>
  <div>
    <div id="page-description">
      <div>
        Type or paste a list of
        <span v-if="domain === 'admitted_students'">
          CSID
        </span>
        <span v-if="domain !== 'admitted_students'">
          Student Identification (<span :aria-hidden="true">SID</span><span class="sr-only">S I D</span>)
        </span>
        numbers below.
      </div>
      <div class="text-medium-emphasis">Example: 9999999990, 9999999991</div>
    </div>
    <div class="mt-3 w-100">
      <v-alert
        v-if="showWarning"
        :id="`${idPrefix}-alert`"
        aria-live="polite"
        class="v-alert-override w-100 mb-5"
        density="compact"
        type="warning"
        variant="tonal"
      >
        <v-alert-title class="font-size-16">
          <div v-if="warning" class="mr-2">{{ warning }}</div>
          <div v-if="sids.length && sidsNotFound.length">{{ sidsNotFound.length === 1 ? 'Remove from list?' : 'Remove these from your list?' }}</div>
          <div v-if="!sids.length || sidsNotFound.length" class="ml-2" :class="{'ms-auto': !sids.length}">
            <v-btn
              id="remove-invalid-sids-btn"
              :aria-label="sids.length ? 'Remove invalid S I Deez' : 'Clear the textarea'"
              class="font-size-16"
              color="primary-darken-1"
              :text="sids.length ? 'Yes' : 'Clear the textarea'"
              variant="text"
              @click="scrub"
            />
          </div>
        </v-alert-title>
        <ul
          v-if="sids.length && sidsNotFound.length && (sidsNotFound.length <= magicNumber)"
          id="sids-not-found"
          aria-label="invalid S I D numbers"
          class="mb-1 pl-6"
        >
          <li v-for="sid in sidsNotFound" :key="sid">{{ sid }}</li>
        </ul>
      </v-alert>
      <v-textarea
        :id="textareaId"
        v-model="textarea"
        :aria-describedby="`${headingId} page-description`"
        aria-label="Student S I D numbers"
        autocomplete="on"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        :density="embedded ? 'compact' : undefined"
        :disabled="isValidating || isSaving"
        :hide-details="embedded"
        :label="embedded ? undefined : 'Enter SIDs here'"
        :max-rows="embedded ? 30 : undefined"
        :rows="embedded ? 8 : undefined"
        variant="outlined"
        @keydown.esc="onEsc"
      />
      <div class="d-flex justify-end pt-3">
        <ProgressButton
          :id="submitButtonId"
          :action="submit"
          :aria-label="resolvedSubmitAriaLabel"
          :disabled="!trim(textarea) || isValidating || isSaving"
          :in-progress="isValidating || isSaving"
          :text="isValidating || isSaving ? 'Adding' : resolvedSubmitText"
        />
        <v-btn
          v-if="showCancel"
          id="btn-cancel-bulk-add-sids"
          :aria-label="`Cancel Add Students to ${describeCuratedGroupDomain(domain)}`"
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
import {each, partition, split, trim, uniq} from 'lodash'
import {computed, onMounted, ref} from 'vue'
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {describeCuratedGroupDomain} from '@/lib/berkeley-utils'
import {validateSids} from '@/api/student'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  onBulkAddSids: {
    required: true,
    type: Function
  },
  domain: {
    default: undefined,
    required: false,
    type: String
  },
  embedded: {
    required: false,
    type: Boolean
  },
  headingId: {
    required: true,
    type: String
  },
  idPrefix: {
    default: 'bulk-add',
    required: false,
    type: String
  },
  isSaving: {
    required: false,
    type: Boolean
  },
  onEsc: {
    default: () => {},
    required: false,
    type: Function
  },
  showCancel: {
    required: false,
    type: Boolean
  },
  submitAriaLabel: {
    default: undefined,
    required: false,
    type: String
  }
})

const currentUser = useContextStore().currentUser
const isValidating = ref(false)
const magicNumber = ref(15)
const showWarning = ref(false)
const sids = ref([])
const sidsNotFound = ref([])
const textarea = ref(undefined)
const warning = ref(undefined)

const textareaId = computed(() => `${props.idPrefix}-sids`)
const submitButtonId = computed(() => `btn-${props.idPrefix}-sids`)
const resolvedSubmitAriaLabel = computed(() => {
  if (props.submitAriaLabel) {
    return props.submitAriaLabel
  }
  return `Add Students to ${describeCuratedGroupDomain(props.domain)}`
})
const resolvedSubmitText = computed(() => {
  if (props.embedded || props.showCancel) {
    return 'Add'
  }
  return 'Next'
})

onMounted(() => {
  putFocusNextTick(textareaId.value)
})

const cancel = () => {
  if (props.showCancel) {
    clearWarning()
    props.onBulkAddSids(null)
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
  alertScreenReader(`${sidsNotFound.value.length} invalid S I Deez removed from textarea.`)
  sidsNotFound.value = []
  clearWarning()
  putFocusNextTick(textareaId.value)
}

const setWarning = message => {
  warning.value = message
  showWarning.value = true
  alertScreenReader(message.replace('SIDs', 'S I Deez'))
  putFocusNextTick('remove-invalid-sids-btn')
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
      putFocusNextTick(textareaId.value)
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
        if (sidsNotFound.value.length) {
          isValidating.value = false
          const label = props.domain === 'admitted_students' ? 'admit' : 'student'
          if (sids.value.length) {
            setWarning(sidsNotFound.value.length === 1 ? `One ${label} not found.` : `${sidsNotFound.value.length} ${label}s not found.`)
          } else {
            setWarning(`No matching ${label}${sidsNotFound.value.length === 1 ? '' : 's'} found.`)
          }
        } else {
          Promise.resolve(props.onBulkAddSids(uniq(sids.value))).then(result => {
            isValidating.value = false
            if (result !== false) {
              sids.value = []
              if (props.embedded) {
                textarea.value = undefined
              }
            }
          }).catch(() => {
            isValidating.value = false
          })
        }
      }).catch(() => {
        isValidating.value = false
      })
    }
  } else {
    setWarning('Please provide one or more SIDs.')
    putFocusNextTick(textareaId.value)
  }
}
</script>

<style>
.v-alert-override {
  .v-alert__prepend {
    padding-top: 3px;
  }
}
</style>
