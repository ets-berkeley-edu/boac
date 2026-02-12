<template>
  <div class="default-margins">
    <h1 id="page-header">Degree Builder</h1>
    <div id="create-degree-description">
      To begin the degree check creation process, input a name below and click enter.
      After clicking the create button, you will be prompted to enter the requirements.
    </div>
    <div class="mt-3 w-sm-75">
      <label id="create-degree-label" class="font-weight-bold font-size-16" for="create-degree-input">Degree Name</label>
      <v-text-field
        id="create-degree-input"
        v-model="templateName"
        aria-describedby="create-degree-input-details"
        :aria-invalid="!!errorMessage"
        autocomplete="on"
        class="mt-2"
        density="comfortable"
        :disabled="isBusy"
        :error="!!errorMessage"
        :error-messages="errorMessage"
        maxlength="255"
        persistent-counter
        required
        :rules="[validate]"
        validate-on="lazy submit"
        @keydown.enter="create"
      >
        <template #counter="{max, value}">
          <CharacterCount :count="toInt(value)" id-prefix="create-degree-name" :max="toInt(max)" />
        </template>
        <template #message="{message}">
          <v-alert
            id="create-degree-name-error"
            class="font-size-14 line-height-normal"
            density="compact"
            role="none"
            type="error"
            variant="tonal"
          >
            <span v-html="message" />
          </v-alert>
        </template>
      </v-text-field>
      <div class="d-flex justify-end pt-2">
        <ProgressButton
          id="start-degree-btn"
          :action="create"
          :aria-disabled="isBusy || !!errorMessage || !trim(templateName)"
          color="primary"
          :disabled="isBusy"
          :in-progress="isBusy"
          :text="isBusy ? 'Saving' : 'Start Degree'"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted, ref, watch} from 'vue'
import {trim} from 'lodash'
import {useRouter} from 'vue-router'
import CharacterCount from '@/components/util/CharacterCount'
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, putFocusNextTick, toInt} from '@/lib/utils'
import {createDegreeTemplate, getDegreeTemplates} from '@/api/degree'
import {useContextStore} from '@/stores/context'
import {validateDegreeTemplateName} from '@/lib/degree-progress'

const contextStore = useContextStore()
const router = useRouter()

const degreeTemplates = ref([])
const errorMessage = ref('')
const isBusy = ref(false)
const templateName = ref('')

watch(templateName, () => errorMessage.value = '')

contextStore.loadingStart()

onMounted(() => {
  getDegreeTemplates().then(data => {
    degreeTemplates.value = data
    contextStore.loadingComplete()
  })
})

const create = () => {
  isBusy.value = true
  if (validate() === true) {
    alertScreenReader('Creating template')
    createDegreeTemplate(trim(templateName.value)).then(data => {
      router.push(`/degree/${data.id}`).then(() => {
        isBusy.value = false
      })
    })
  } else {
    putFocusNextTick('create-degree-input')
    isBusy.value = false
  }
}

const validate = () => {
  const validationReport = validateDegreeTemplateName(templateName.value, degreeTemplates.value)
  errorMessage.value = validationReport.message
  return validationReport.valid || validationReport.message
}
</script>
