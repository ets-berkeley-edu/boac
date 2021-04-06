<template>
  <div>
    <div v-if="!degreeId" class="ml-3 mr-3 mt-3">
      <StartDegree
        :create="create"
      />
    </div>

    <div v-if="degreeId">
      <!-- Present components for the degree creation -->
      Placeholder text
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import StartDegree from '@/components/degree-progress/StartDegree.vue'
import Util from '@/mixins/Util'
import {createDegreeTemplate} from '@/api/degree'

export default {
  name: 'CreateDegreeTemplate',
  components: {StartDegree},
  mixins: [Context, Util],
  data: () => ({
    isSaving: false,
    name: '',
    error: undefined,
    degreeId: undefined,
  }),
  watch: {
    name() {
      this.error = undefined
      this.degreeId = ''
    },
    reset() {
      this.error = undefined
      this.name = ''
    }
  },
  methods: {
    create(name) {
      createDegreeTemplate(name)
        .then(degree => {
          this.isSaving = false
          this.$router.push(`/degree/${degree.id}`)
          console.log(degree.id)
          this.degreeId = degree.id
        })
    }
  },
  mounted() {
    if (this.$config.featureFlagDegreeCheck) {
      this.degreeId = this.$_.get(this.$route, 'params.id') || ''
    } else {
      this.$router.push({path: '/404'})
    }
  }
}
</script>
