<template>
  <div v-if="!loading" class="ml-3 mr-3 mt-3">
    <h1 class="page-section-header">Degree Builder</h1>
    <div id="create-degree-description">
      To begin the degree check creation process, input a name below and click enter.
      After clicking the create button, you will be prompted to enter the requirements.
    </div>
    <form class="mt-3" @submit.prevent="create">
      <label id="create-degree-label" class="font-weight-bold font-size-16" for="create-degree-input">Degree Name</label>
      <b-form-input
        id="create-degree-input"
        v-model="templateName"
        aria-labelledby="create-degree-label"
        class="w-50"
        :disabled="isBusy"
        maxlength="255"
      />
      <div class="pl-2">
        <span class="faint-text font-size-12">255 character limit <span v-if="templateName.length">({{ 255 - templateName.length }} left)</span></span>
        <span v-if="templateName.length === 255" class="sr-only" aria-live="polite">
          Degree name cannot exceed 255 characters.
        </span>
      </div>
      <div v-if="error" class="error-message-container mt-2 p-3">
        <span v-html="error"></span>
      </div>
      <div class="mt-0">
        <b-btn
          id="start-degree-btn"
          class="btn-primary-color-override h-100 mr-0 mt-3"
          :disabled="isBusy || !!error || !_trim(templateName)"
          variant="primary"
          @click.prevent="create"
        >
          <span v-if="isBusy"><v-progress-circular class="mr-1" size="small" /> Saving</span>
          <span v-if="!isBusy">Start Degree</span>
        </b-btn>
      </div>
    </form>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {createDegreeTemplate, getDegreeTemplates} from '@/api/degree'

export default {
  name: 'CreateDegreeTemplate',
  mixins: [Context, Util],
  data: () => ({
    error: undefined,
    isBusy: false,
    templateName: ''
  }),
  watch: {
    templateName() {
      this.error = null
    }
  },
  mounted() {
    this.loadingComplete()
    this.alertScreenReader('Create degree template')
  },
  methods: {
    create() {
      this.isBusy = true
      getDegreeTemplates().then(data => {
        const lower = this.templateName.trim().toLowerCase()
        if (this._map(data, 'name').findIndex(s => s.toLowerCase() === lower) === -1) {
          this.alertScreenReader('Creating template')
          createDegreeTemplate(this.templateName).then(data => {
            this.$router.push(`/degree/${data.id}`)
            this.isBusy = false
          })
        } else {
          this.error = `A degree named <span class="font-weight-500">${this.templateName}</span> already exists. Please choose a different name.`
          this.alertScreenReader(this.error)
          this.isBusy = false
        }
      })
    }
  }
}
</script>
