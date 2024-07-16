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
        class="w-50"
        :disabled="isBusy"
        maxlength="255"
      />
      <div class="pl-2">
        <span class="text-grey font-size-12">255 character limit <span v-if="templateName.length">({{ 255 - templateName.length }} left)</span></span>
        <span v-if="templateName.length === 255" class="sr-only" aria-live="polite">
          Degree name cannot exceed 255 characters.
        </span>
      </div>
      <div v-if="error" class="error-message-container mt-2 p-3">
        <span v-html="error"></span>
      </div>
      <div class="mt-0">
        <v-btn
          id="start-degree-btn"
          class="h-100 mr-0 mt-3"
          color="primary"
          :disabled="isBusy || !!error || !trim(templateName)"
          @click.prevent="create"
        >
          <span v-if="isBusy"><v-progress-circular class="mr-1" size="small" /> Saving</span>
          <span v-if="!isBusy">Start Degree</span>
        </v-btn>
      </div>
    </form>
  </div>
</template>

<script setup>
import {alertScreenReader} from '@/lib/utils'
import {createDegreeTemplate, getDegreeTemplates} from '@/api/degree'
import {onMounted, ref, watch} from 'vue'
import {map, trim} from 'lodash'
import {useRouter} from 'vue-router'

const error = ref('')
const isBusy = ref(false)
const templateName = ref('')

watch(templateName, () => error.value = null)

onMounted(() => alertScreenReader('Create degree template'))

const create = () => {
  isBusy.value = true
  getDegreeTemplates().then(data => {
    const lower = templateName.value.trim().toLowerCase()
    if (map(data, 'name').findIndex(s => s.toLowerCase() === lower) === -1) {
      alertScreenReader('Creating template')
      createDegreeTemplate(templateName.value).then(data => {
        useRouter().push(`/degree/${data.id}`)
        isBusy.value = false
      })
    } else {
      error.value = `A degree named <span class="font-weight-500">${templateName.value}</span> already exists. Please choose a different name.`
      alertScreenReader(error.value)
      isBusy.value = false
    }
  })
}
</script>
