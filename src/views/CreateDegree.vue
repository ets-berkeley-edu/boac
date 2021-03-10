<template>
  <div class="ml-3 mr-3 mt-3">
    <h1>Degree Builder</h1>
    <span class="sr-only">Degree Builder</span>
    <div id="create-degree-description">
      <span class="sr-only">To begin the degree check creation process, input a name below and click enter. After clicking the create button, you will be prompted to enter the requirements.</span>
      To begin the degree check creation process, input a name below and click enter. After clicking the create button, you will be prompted to enter the requirements.
    </div>

    <form @submit.prevent="createDegree">
      <span class="sr-only">Cohort </span>Name:</label>
      <h2>Degree Name</h2>
      <span class="sr-only">Degree Name</span>
      <div class="w-25">
        <b-form-input
          id="degree-name-input"
          v-model="name"
          aria-labelledby="lable-of-degree-name-input"
          class="degree-create-degree-input"
          maxlength="255"
          size="lg"
        >
        </b-form-input>
      </div>
    </form>
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
  }),
  methods: {
    createDegree: function() {
      // make call to create degree
    }
  }


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

h2 {
  font-size: 13px;
  font-weight: bold;
}