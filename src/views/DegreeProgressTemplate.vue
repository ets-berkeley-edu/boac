<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner />
    <div v-if="!loading">
      <h1 v-if="!templateId">Degree Builder</h1>
      <h1 v-if="templateId">{{ degreeName }}</h1>
      <hr />
      <UnitRequirements v-if="templateId" template-id="templateId" />
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DegreeProgressEditSession from '@/mixins/DegreeProgressEditSession'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import UnitRequirements from '@/components/degree-progress/UnitRequirements'
import Util from '@/mixins/Util'

export default {
  name: 'DegreeProgressTemplate',
  components: {
    Spinner,
    UnitRequirements
  },
  mixins: [Context, DegreeProgressEditSession, Loading, Util],
  mounted() {
    const id = this.toInt(this.$_.get(this.$route, 'params.id'))
    this.init(id).then(() => {
      this.setPageTitle(this.degreeName)
      this.loaded(this.getLoadedAlert())
      this.putFocusNextTick('add-unit-requirement')
    })
  },
  methods: {
    getLoadedAlert() {
      if (!this.templateId) {
        return 'Create degree page has loaded'
      } else {
        return `Degree ${this.degreeName || ''} has loaded`
      }
    }
  }
}
</script>