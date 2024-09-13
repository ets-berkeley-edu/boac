<template>
  <v-card
    v-show="isOpen"
    flat
  >
    <div class="align-center align-top d-flex flex-wrap">
      <v-text-field
        v-if="isOpen"
        id="rename-cohort-input"
        v-model="name"
        aria-label="Cohort name, 255 characters or fewer"
        :aria-required="true"
        class="v-input-details-override mr-3"
        counter="255"
        density="comfortable"
        :disabled="isSaving"
        hide-details
        label="Cohort Name"
        :maxlength="maxlength"
        persistent-counter
        required
        :rules="[validationRules.valid]"
        validate-on="lazy input"
        @keyup.enter="submit"
        @keyup.esc="cancel"
      />
      <div class="d-flex justify-end">
        <ProgressButton
          id="rename-cohort-confirm"
          :action="submit"
          :disabled="isInvalid || isSaving"
          :in-progress="isSaving"
          size="large"
          text="Rename"
        />
        <v-btn
          id="rename-cohort-cancel"
          class="ml-1"
          :disabled="isSaving"
          size="large"
          text="Cancel"
          variant="text"
          @click="cancel"
        />
      </div>
    </div>
    <div id="name-cohort-counter" aria-live="polite" class="text-left font-size-13 text-no-wrap ml-4 mt-1">
      <span class="sr-only">Cohort name has a </span>{{ maxlength }} character limit <span v-if="size(name)">({{ maxlength - size(name) }} left)</span>
    </div>
  </v-card>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader} from '@/lib/utils'
import {putFocusNextTick, setPageTitle} from '@/lib/utils'
import {saveCohort} from '@/api/cohort'
import {size} from 'lodash'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {validateCohortName} from '@/lib/cohort'
import {ref, watch} from 'vue'

const props = defineProps({
  cancel: {
    type: Function,
    required: true
  },
  isOpen: {
    type: Boolean,
    required: true
  }
})

const cohortStore = useCohortStore()

const isInvalid = ref(true)
const isSaving = ref(false)
const maxlength = ref(255)
const name = ref('')
const validationRules = {
  valid: name => {
    const valid = validateCohortName({id: cohortStore.cohortId, name})
    isInvalid.value = true !== valid
    return valid
  }
}

watch(() => props.isOpen, value => {
  if (value) {
    name.value = cohortStore.cohortName
  }
})

const submit = () => {
  if (true !== validateCohortName({id: cohortStore.cohortId, name: name.value})) {
    putFocusNextTick('rename-cohort-input')
  } else {
    isSaving.value = true
    alertScreenReader('Renaming cohort')
    cohortStore.renameCohort(name.value)
    saveCohort(cohortStore.cohortId, cohortStore.cohortName, cohortStore.filters).then(() => {
      isSaving.value = false
      alertScreenReader(`Cohort renamed to '${name.value}'`)
      setPageTitle(name.value)
      cohortStore.setEditMode(null)
      putFocusNextTick('cohort-name')
    })
  }
}
</script>
