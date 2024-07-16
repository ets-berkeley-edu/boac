<template>
  <b-modal
    v-model="showModal"
    :no-close-on-backdrop="true"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @cancel.prevent="cancel"
    @hide.prevent="cancel"
    @shown="putFocusNextTick('modal-header')"
  >
    <ModalHeader text="Name Your Degree Copy" />
    <form @submit.prevent="createClone" @keydown.esc="cancel">
      <div class="ma-3">
        <label id="degree-name-input-label" for="degree-name-input">Degree Name:</label>
        <b-form-input
          id="degree-name-input"
          v-model="name"
          aria-labelledby="degree-name-input-label"
          class="name-input"
          :disabled="isSaving"
          maxlength="255"
          size="lg"
          @keypress.enter.prevent="() => name.length && createClone()"
          @keyup.esc="cancel"
        />
        <div class="pl-2 pt-1">
          <span class="text-grey font-size-12"><span class="sr-only">Degree name has a </span>255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></span>
          <span
            v-if="name.length === 255"
            aria-live="polite"
            class="sr-only"
            role="alert"
          >
            Degree name cannot exceed 255 characters.
          </span>
        </div>
        <div v-if="error" class="error-message-container mt-2 p-3">
          <span v-html="error"></span>
        </div>
      </div>
      <div class="modal-footer mb-0 mr-2 pb-0 pl-0">
        <b-btn
          id="clone-confirm"
          :disabled="!name.trim().length || isSaving || !!error || (templateToClone.name === name)"
          class="btn-primary-color-override"
          variant="primary"
          @click.prevent="createClone"
        >
          <span v-if="isSaving"><v-progress-circular class="mr-1" size="small" /> Saving</span>
          <span v-if="!isSaving">Save Copy</span>
        </b-btn>
        <b-btn
          id="clone-cancel"
          :disabled="isSaving"
          variant="link"
          @click="cancel"
        >
          Cancel
        </b-btn>
      </div>
    </form>
  </b-modal>
</template>

<script setup>
import ModalHeader from '@/components/util/ModalHeader.vue'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {cloneDegreeTemplate, getDegreeTemplates} from '@/api/degree'
import {computed, ref, watch} from 'vue'
import {map} from 'lodash'

const props = defineProps({
  cancel: {
    required: true,
    type: Function
  },
  afterCreate: {
    required: true,
    type: Function
  },
  templateToClone: {
    required: true,
    type: Object
  }
})

const error = ref(undefined)
const isSaving = ref(false)
const name = ref(props.templateToClone.name)
const showModal = computed({
  get() {
    return !!props.templateToClone
  },
  set(value) {
    if (!value) {
      props.cancel()
    }
  }
})

watch(name, () => {
  error.value = null
})

const createClone = () => {
  isSaving.value = true
  getDegreeTemplates().then(data => {
    const lower = name.value.trim().toLowerCase()
    if (map(data, 'name').findIndex(s => s.toLowerCase() === lower) === -1) {
      alertScreenReader('Cloning template')
      cloneDegreeTemplate(props.templateToClone.id, name.value).then(data => {
        props.afterCreate(data)
        isSaving.value = false
      })
    } else {
      error.value = `A degree named <span class="font-weight-500">${name.value}</span> already exists. Please choose a different name.`
      alertScreenReader(this.error)
      isSaving.value = false
    }
  })
}
</script>

<style scoped>
.name-input {
  border: 1px solid #66afe9;
  border-radius: 4px;
  box-sizing: border-box;
}
</style>
