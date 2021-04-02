<template>
  <div class="ml-3 mr-3 mt-3">
    <h1>Degree Builder</h1>
    <span class="sr-only">Degree Builder</span>
    <div id="create-degree-description">
      <span>To begin the degree check creation process, input a name below and click enter. After clicking the create button, you will be prompted to enter the requirements.</span>
    </div>

    <form class="mt-3" @submit.prevent="createDegree">
      <label id="label-of-create-degree-input" for="create-degree-input">Degree Name</label>
      <span class="sr-only">Degree Name</span>
      <b-form-input
        id="create-degree-input"
        v-model="name"
        aria-labelledby="label-of-create-degree-input"
        class="create-degree-input-name w-25"
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
        v-if="name.length === 255"
        class="sr-only"
        aria-live="polite"
      >
        Degree name cannot exceed 255 characters.
      </div>

      <div class="mt-0">
        <b-btn
          id="start-degree"
          :disabled="!name.length"
          class="btn-primary-color-override h-100 mr-0 mt-3"
          variant="primary"
          @click.prevent="createDegree"
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

export default {
  name: 'CreateDegree',
  mixins: [Context, Loading, Util],
  data: () => ({
    name: '',
    error: undefined,
  }),
  watch: {
    name() {
      this.error = undefined
    }
  },
  methods: {
    createDegree: function() {
      // validate the name if needed then update name, error
      if (!this.error) {
        // make call to create degree

      }
    }
  },
  mounted() {
    if (this.$config.featureFlagDegreeCheck) {
      this.loaded('Create degree page loaded')
    } else {
      this.$router.push({path: '/404'})
    }
  }
}
</script>

<style>
#label-of-create-degree-input {
  font-weight: bold;
  font-size: 16px;
}
</style>
