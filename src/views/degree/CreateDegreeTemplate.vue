<template>
  <div class="ml-3 mr-3 mt-3">
    <StartDegree :create="create" />
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import StartDegree from '@/components/degree/StartDegree.vue'
import Util from '@/mixins/Util'
import {createDegreeTemplate} from '@/api/degree'

export default {
  name: 'CreateDegreeTemplate',
  components: {StartDegree},
  mixins: [Context, Util],
  data: () => ({
    isSaving: false,
    name: '',
    error: undefined
  }),
  watch: {
    name() {
      this.error = undefined
    }
  },
  methods: {
    create(name) {
      createDegreeTemplate(name)
        .then(degree => {
          this.isSaving = false
          this.$router.push(`/degree/${degree.id}`)
        })
    }
  }
}
</script>
