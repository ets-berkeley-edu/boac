<template>
  <div>
    <Spinner />
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'

export default {
  name: 'DegreeChecks',
  components: {Spinner},
  mixins: [Context, Loading, Util],
  created() {
    if (this.$config.featureFlagDegreeCheck) {
      // TODO: make an API call (BOAC-3935)
      this.$_.noop()
    } else {
      this.$router.push({path: '/404'})
    }
  },
}
</script>