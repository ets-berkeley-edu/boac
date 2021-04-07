<template>
  <div v-if="!loading" class="ml-3 mr-3 mt-3">
    <h1>Degree Builder</h1>
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
        maxlength="255"
      />
      <div
        v-if="templateName.length === 255"
        class="sr-only"
        aria-live="polite"
      >
        Degree name cannot exceed 255 characters.
      </div>

      <div class="mt-0">
        <b-btn
          id="start-degree-btn"
          class="btn-primary-color-override h-100 mr-0 mt-3"
          :disabled="!$_.trim(templateName)"
          variant="primary"
          @click.prevent="create"
        >
          Start Degree
          <span class="sr-only">Submit Start Degree</span>
        </b-btn>
      </div>
    </form>
  </div>
</template>

<script>
import Loading from '@/mixins/Loading'
import {createDegreeTemplate} from '@/api/degree'

export default {
  name: 'CreateDegreeTemplate',
  mixins: [Loading],
  data: () => ({
    templateName: ''
  }),
  mounted() {
    this.loaded('Create degree template')
  },
  methods: {
    create() {
      this.$announcer.set('Creating template', 'polite')
      createDegreeTemplate(this.templateName).then(data => {
        this.$router.push(`/degree/${data.id}`)
      })
    }
  }
}
</script>
