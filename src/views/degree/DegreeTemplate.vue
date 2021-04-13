<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner />
    <div v-if="!loading">
      <h1 v-if="!templateId">Degree Builder</h1>
      <h1 v-if="templateId">{{ degreeName }}</h1>
      <hr />
      <UnitRequirements v-if="templateId" template-id="templateId" />
      <hr />
      <b-container class="px-0 mx-0">
        <b-row>
          <b-col
            v-for="position in [1, 2, 3]"
            :key="position"
            class="degree-progress-column"
          >
            <TemplateCategoryColumn :position="position" />
          </b-col>
        </b-row>
      </b-container>
      <div v-if="$config.isVueAppDebugMode" class="pt-5">
        <DebugTemplate />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DebugTemplate from '@/components/degree/DebugTemplate'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import TemplateCategoryColumn from '@/components/degree/TemplateCategoryColumn'
import UnitRequirements from '@/components/degree/UnitRequirements'
import Util from '@/mixins/Util'

export default {
  name: 'DegreeTemplate',
  components: {
    DebugTemplate,
    Spinner,
    TemplateCategoryColumn,
    UnitRequirements
  },
  mixins: [Context, DegreeEditSession, Loading, Util],
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

<style>
.degree-progress-column {
  min-width: 300px;
  padding-bottom: 10px;
}
</style>
