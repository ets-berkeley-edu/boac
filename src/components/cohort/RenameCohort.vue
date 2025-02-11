<template>
  <v-card class="py-1 w-100" flat>
    <div class="d-flex flex-wrap">
      <v-text-field
        id="rename-cohort-input"
        v-model="name"
        :aria-invalid="!name"
        aria-label="Cohort name"
        autocomplete="off"
        class="v-input-details-override mr-3"
        counter="255"
        density="comfortable"
        :disabled="isSaving"
        label="Cohort Name"
        :maxlength="maxlength"
        persistent-counter
        required
        :rules="[() => isValidName]"
        validate-on="lazy input"
        @keyup.enter="submit"
        @keyup.esc="cancel"
      >
        <template #counter>
          <div>
            {{ size(name) ? `${maxlength} character limit (${maxlength - size(name)} left)` : `${maxlength} character limit` }}
          </div>
        </template>
      </v-text-field>
      <span
        v-if="size(name) === maxlength"
        aria-live="polite"
        class="sr-only"
        role="alert"
      >
        Cohort name cannot exceed {{ maxlength }} characters.
      </span>
      <div>
        <ProgressButton
          id="rename-cohort-confirm"
          :action="submit"
          aria-label="Rename Cohort"
          class="mr-1"
          :disabled="isValidName !== true || isSaving"
          :in-progress="isSaving"
          size="large"
          :text="isSaving ? 'Renaming' : 'Rename'"
        />
        <v-btn
          id="rename-cohort-cancel"
          aria-label="Cancel Rename Cohort"
          :disabled="isSaving"
          size="large"
          text="Cancel"
          variant="text"
          @click="cancel"
        />
      </div>
    </div>
  </v-card>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {size} from 'lodash'
import {storeToRefs} from 'pinia'
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, putFocusNextTick, setPageTitle} from '@/lib/utils'
import {saveCohort} from '@/api/cohort'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {validateCohortName} from '@/lib/cohort'

const cohortStore = useCohortStore()
const {cohortId, cohortName, filters} = storeToRefs(cohortStore)
const isSaving = ref(false)
const isValidName = computed(() => validateCohortName({id: cohortId.value, name: name.value}))
const maxlength = ref(255)
const name = ref(undefined)

onMounted(() => {
  name.value = cohortName.value
})

const cancel = () => {
  cohortStore.setEditMode(null)
  alertScreenReader('Canceled rename cohort')
  putFocusNextTick('rename-cohort-button')
}

const submit = () => {
  if (true !== validateCohortName({id: cohortId.value, name: name.value})) {
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
</script>
