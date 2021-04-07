<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner />
    <div v-if="!loading">
      <h1 v-if="!templateId">Degree Builder</h1>
      <h1 v-if="templateId">{{ degreeName }}</h1>
      <hr />
      <UnitRequirements v-if="templateId" template-id="templateId" />
      <hr />
      <RequirementCategories />
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Loading from '@/mixins/Loading'
import RequirementCategories from '@/components/degree/RequirementCategories'
import Spinner from '@/components/util/Spinner'
import UnitRequirements from '@/components/degree/UnitRequirements'
import Util from '@/mixins/Util'

export default {
  name: 'DegreeProgressTemplate',
  components: {
    Spinner,
    RequirementCategories,
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
.degree-progress-btn-link {
  display: flex;
  flex-direction: row-reverse;
}
.degree-progress-btn-link.disabled {
  color: #6c757d !important;
}
.degree-progress-column {
  min-width: 300px;
  padding-bottom: 10px;
}
.degree-progress-pill {
  background-color: #999;
  color: #fff;
  font-weight: 500;
  text-align: center;
  text-transform: uppercase;
  white-space: nowrap;
}
</style>
