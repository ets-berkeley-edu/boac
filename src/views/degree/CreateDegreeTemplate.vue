<template>
  <div class="default-margins">
    <h1 class="page-section-header">Degree Builder</h1>
    <div id="create-degree-description">
      To begin the degree check creation process, input a name below and click enter.
      After clicking the create button, you will be prompted to enter the requirements.
    </div>
    <form class="mt-3" @submit.prevent="create">
      <label id="create-degree-label" class="font-weight-bold font-size-16" for="create-degree-input">Degree Name</label>
      <v-text-field
        id="create-degree-input"
        v-model="templateName"
        aria-labelledby="create-degree-label"
        autocomplete="off"
        class="mt-2 w-75"
        density="comfortable"
        :disabled="isBusy"
        hide-details
        maxlength="255"
        @keydown.enter="create"
      />
      <div class="pl-2">
        <span class="text-grey-darken-4 font-size-12">255 character limit <span v-if="templateName.length">({{ 255 - templateName.length }} left)</span></span>
        <span
          v-if="templateName.length === 255"
          aria-live="polite"
          class="sr-only"
          role="alert"
        >
          Degree name cannot exceed 255 characters.
        </span>
      </div>
      <div v-if="error" class="error-container mt-2 px-5 py-3 w-75" v-html="error" />
      <div class="d-flex justify-end pt-2 w-75">
        <ProgressButton
          id="start-degree-btn"
          :action="create"
          color="primary"
          :disabled="isBusy || !!error || !trim(templateName)"
          :in-progress="isBusy"
          :text="isBusy ? 'Saving' : 'Start Degree'"
        />
      </div>
    </form>
  </div>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton'
import router from '@/router'
import {alertScreenReader} from '@/lib/utils'
import {createDegreeTemplate, getDegreeTemplates} from '@/api/degree'
import {onMounted, ref, watch} from 'vue'
import {map, trim} from 'lodash'

const error = ref('')
const isBusy = ref(false)
const templateName = ref('')

watch(templateName, () => error.value = null)

onMounted(() => alertScreenReader('Create degree template'))

const create = () => {
  if (!error.value && trim(templateName.value)) {
    isBusy.value = true
    getDegreeTemplates().then(data => {
      const lower = trim(templateName.value).toLowerCase()
      if (map(data, 'name').findIndex(s => s.toLowerCase() === lower) === -1) {
        alertScreenReader('Creating template')
        createDegreeTemplate(trim(templateName.value)).then(data => {
          router.push(`/degree/${data.id}`).then(() => {
            isBusy.value = false
          })
        })
      } else {
        error.value = `A degree named <span class="font-weight-500">${templateName.value}</span> already exists. Please choose a different name.`
        alertScreenReader(error.value)
        isBusy.value = false
      }
    })
  }
}
</script>

<style scoped>
.error-container {
  background-color: #efd6d6;
  border-radius: 4px;
  color: #9b393a;
}
</style>
