<template>
  <v-card class="py-1 w-100" flat>
    <div class="d-flex flex-wrap flex-sm-nowrap">
      <v-text-field
        id="rename-cohort-input"
        v-model="name"
        aria-describedby="rename-cohort-input-messages"
        :aria-invalid="!!errorMessage"
        autocomplete="on"
        class="flex-1-1 mr-3 mb-3"
        counter="255"
        density="comfortable"
        :disabled="isSaving"
        :error="!!errorMessage"
        :error-messages="errorMessage"
        label="Cohort Name"
        :maxlength="maxlength"
        persistent-counter
        required
        :rules="[validate]"
        validate-on="lazy invalid-input"
        @keyup.enter="submit"
        @keyup.esc="cancel"
      >
        <template #counter="{max, value}">
          <CharacterCount :count="toInt(value)" id-prefix="rename-cohort" :max="toInt(max)" />
        </template>
        <template #message="{message}">
          <v-alert
            id="rename-cohort-error"
            class="font-size-14 line-height-normal"
            density="compact"
            role="none"
            :text="message"
            type="error"
            variant="tonal"
          />
        </template>
      </v-text-field>
      <div class="d-flex ml-auto w-100 w-sm-auto">
        <ProgressButton
          id="rename-cohort-confirm"
          :action="submit"
          :ariadisabled="isEmpty(name) || isInvalid"
          aria-label="Rename Cohort"
          class="mr-1"
          :class="{'w-50': xs}"
          :disabled="isSaving"
          height="48px"
          :in-progress="isSaving"
          :text="isSaving ? 'Saving' : 'Save'"
        />
        <v-btn
          id="rename-cohort-cancel"
          aria-label="Cancel Rename Cohort"
          :class="{'w-50': xs}"
          :disabled="isSaving"
          height="48px"
          text="Cancel"
          variant="text"
          @click="cancel"
        />
      </div>
    </div>
  </v-card>
</template>

<script setup>
import {isEmpty} from 'lodash'
import {onMounted, ref} from 'vue'
import {storeToRefs} from 'pinia'
import {useDisplay} from 'vuetify'
import CharacterCount from '@/components/util/CharacterCount'
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, putFocusNextTick, setPageTitle, toInt} from '@/lib/utils'
import {saveCohort} from '@/api/cohort'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {validateCohortName} from '@/lib/cohort'

const cohortStore = useCohortStore()
const {cohortId, cohortName, filters} = storeToRefs(cohortStore)
const errorMessage = ref('')
const isInvalid = ref(true)
const isSaving = ref(false)
const maxlength = ref(255)
const name = ref('')
const {xs} = useDisplay()

onMounted(() => {
  name.value = cohortName.value
})

const cancel = () => {
  reset()
  cohortStore.setEditMode(null)
  alertScreenReader('Canceled rename cohort')
  putFocusNextTick('rename-cohort-button')
}

const reset = () => {
  isSaving.value = false
  name.value = ''
  errorMessage.value = ''
  isInvalid.value = false
}

const submit = () => {
  if (true !== validate()) {
    putFocusNextTick('rename-cohort-input')
  } else {
    isSaving.value = true
    alertScreenReader('Renaming cohort')
    cohortStore.renameCohort(name.value)
    saveCohort(cohortId.value, cohortName.value, filters.value).then(() => {
      isSaving.value = false
      alertScreenReader(`Cohort renamed to '${name.value}'`)
      setPageTitle(name.value)
      cohortStore.setEditMode(null)
      putFocusNextTick('rename-cohort-button')
    })
  }
}

const validate = () => {
  const result = validateCohortName({id: cohortId.value, name: name.value})
  if (result === true) {
    errorMessage.value = ''
    isInvalid.value = false
  } else {
    errorMessage.value = result
    isInvalid.value = true
  }
  return result
}
</script>
