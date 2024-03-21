<template>
  <v-expand-transition>
    <v-card v-show="useCohortStore().editMode === 'rename'">
      <div class="d-flex align-top">
        <form @submit.prevent="submitRename">
          <v-text-field
            id="rename-cohort-input"
            v-model="name"
            aria-label="Cohort name, 255 characters or fewer"
            aria-required="true"
            class="mr-2"
            counter="255"
            density="compact"
            maxlength="255"
            required
            type="text"
            persistent-counter
            :rules="[validationRules.required, validationRules.maxLength]"
            validate-on="blur"
            variant="outlined"
            @keyup.esc="cancel"
          >
            <template #counter="{max, value}">
              <div id="name-template-counter" aria-live="polite" class="font-size-13 text-no-wrap my-1">
                <span class="sr-only">Cohort name has a </span>{{ max }} character limit <span v-if="value">({{ max - value }} left)</span>
              </div>
            </template>
          </v-text-field>
        </form>
        <v-btn
          id="rename-confirm"
          :disabled="!name"
          color="primary"
          @click.prevent="submit"
        >
          Rename
        </v-btn>
        <v-btn
          id="rename-cancel"
          variant="plain"
          @click="cancel"
        >
          Cancel
        </v-btn>
      </div>
    </v-card>
  </v-expand-transition>
</template>

<script setup>
import {useCohortStore} from '@/stores/cohort-edit-session'
</script>

<script>
export default {
  name: 'RenameCohort',
  props: {
    cancel: {
      type: Function,
      required: true
    },
    error: {
      default: undefined,
      type: String,
      required: false
    },
    submit: {
      type: Function,
      required: true
    }
  },
  data: () => ({
    name: '',
    isSaving: false,
    validationRules: {
      required: value => !!value || 'Cohort name is required',
      maxLength: value => (!value || value.length <= 255) || 'Cohort name cannot exceed 255 characters.',
    }
  }),
}
</script>
