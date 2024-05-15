<template>
  <v-card
    v-show="isOpen"
    flat
  >
    <div class="align-center d-flex flex-column flex-md-row align-top">
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
        variant="outlined"
        @keyup.enter="submit"
        @keyup.esc="cancel"
      />
      <div class="d-flex justify-end">
        <ProgressButton
          id="rename-confirm"
          :action="submit"
          :disabled="isInvalid || isSaving"
          :in-progress="isSaving"
          size="large"
          text="Rename"
        />
        <v-btn
          id="rename-cancel"
          :disabled="isSaving"
          size="large"
          text="Cancel"
          variant="plain"
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
import {size} from 'lodash'
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
    maxlength: 255,
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
