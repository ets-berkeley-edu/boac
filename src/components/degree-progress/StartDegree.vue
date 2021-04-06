<template>
  <div v-if="!loading" class="mr-3 mt-3">
    <h1>Degree Builder</h1>
    <div id="create-degree-description">
      To begin the degree check creation process, input a name below and click enter.
      After clicking the create button, you will be prompted to enter the requirements.
    </div>

    <form class="mt-3" @submit.prevent="createDegreeTemplate">
      <label id="label-of-create-degree-input" class="font-weight-bold font-size-16" for="create-degree-input">Degree Name</label>
      <b-form-input
        id="create-degree-input"
        v-model="degreeTemplateName"
        aria-labelledby="label-of-create-degree-input"
        class="create-degree-input-name w-50"
        maxlength="255"
        size="lg"
      />
      <div
        v-if="error"
        id="create-error"
        class="has-error"
        aria-live="polite"
        role="alert"
      >
        {{ error }}
      </div>
      <div
        v-if="degreeTemplateName.length === 255"
        class="sr-only"
        aria-live="polite"
      >
        Degree name cannot exceed 255 characters.
      </div>

      <div class="mt-0">
        <b-btn
          id="start-degree-btn"
          class="btn-primary-color-override h-100 mr-0 mt-3"
          :disabled="!$_.trim(degreeTemplateName)"
          variant="primary"
          @click.prevent="createDegreeTemplate"
        >
          Start Degree
          <span class="sr-only">Submit Start Degree</span>
        </b-btn>
      </div>
    </form>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading'
import Util from '@/mixins/Util'
import Validator from '@/mixins/Validator'

export default {
  name: 'StartDegree',
  mixins: [Context, Loading, Util, Validator],
  props: {
    create: Function,
  },
  data: () => ({
    error: undefined,
    degreeTemplateName: ''
  }),
  watch: {
    degreeTemplateName() {
      this.error = undefined
    }
  },
  mounted() {
    this.loaded('Create degree page loaded')
  },
  methods: {
    reset() {
      this.error = undefined
      this.degreeTemplateName = ''
    },
    createDegreeTemplate: function(){
      this.error = this.validateDegreeTemplateName({degreeTemplateName: this.degreeTemplateName})
      if (!this.error) {
        this.create(this.degreeTemplateName)
        this.reset()
      }
    }
  }
}
</script>
