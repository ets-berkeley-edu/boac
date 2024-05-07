<template>
  <v-card
    v-show="isOpen"
    class="py-3"
    flat
  >
    <div class="d-flex flex-column flex-md-row align-top">
      <form class="w-100 mb-2" @submit.prevent="submitRename">
        <v-text-field
          v-if="isOpen"
          id="rename-cohort-input"
          v-model="name"
          aria-label="Cohort name, 255 characters or fewer"
          aria-required="true"
          class="v-input-details-override mr-2"
          counter="255"
          density="compact"
          :disabled="isSaving"
          label="Cohort Name"
          maxlength="255"
          required
          type="text"
          persistent-counter
          :rules="[validationRules.valid]"
          validate-on="lazy input"
          variant="outlined"
          @keyup.esc="cancel"
        >
          <template #counter="{max, value}">
            <div id="name-cohort-counter" aria-live="polite" class="font-size-13 text-no-wrap ml-2 mt-1">
              <span class="sr-only">Cohort name has a </span>{{ max }} character limit <span v-if="value">({{ max - value }} left)</span>
            </div>
          </template>
        </v-text-field>
      </form>
      <div class="d-flex justify-end">
        <ProgressButton
          id="rename-confirm"
          :action="submit"
          :disabled="isInvalid || isSaving"
          :in-progress="isSaving"
        >
          Rename
        </ProgressButton>
        <v-btn
          id="rename-cancel"
          class="ml-1"
          :disabled="isSaving"
          variant="plain"
          @click="cancel"
        >
          Cancel
        </v-btn>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton'
</script>

<script>
import {alertScreenReader} from '@/lib/utils'
import {putFocusNextTick, setPageTitle} from '@/lib/utils'
import {saveCohort} from '@/api/cohort'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {validateCohortName} from '@/lib/cohort'

export default {
  name: 'RenameCohort',
  props: {
    cancel: {
      type: Function,
      required: true
    },
    isOpen: {
      type: Boolean,
      required: true
    }
  },
  data: () => ({
    isInvalid: true,
    isSaving: false,
    name: '',
    validationRules: {}
  }),
  watch: {
    isOpen(val) {
      if (val) {
        this.name = useCohortStore().cohortName
      }
    }
  },
  created() {
    this.validationRules = {
      valid: name => {
        const valid = validateCohortName({id: useCohortStore().cohortId, name})
        this.isInvalid = true !== valid
        return valid
      }
    }
  },
  methods: {
    submit() {
      const cohort = useCohortStore()
      if (true !== validateCohortName({id: cohort.cohortId, name: this.name})) {
        putFocusNextTick('rename-cohort-input')
      } else {
        this.isSaving = true
        alertScreenReader('Renaming cohort')
        cohort.renameCohort(this.name)
        saveCohort(cohort.cohortId, cohort.cohortName, cohort.filters).then(() => {
          this.isSaving = false
          alertScreenReader(`Cohort renamed to '${this.name}'`)
          setPageTitle(this.name)
          cohort.setEditMode(null)
          putFocusNextTick('cohort-name')
        })
      }
    }
  }
}
</script>
