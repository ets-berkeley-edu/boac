<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner />
    <div v-if="!loading">
      <div class="border-bottom pb-3">
        <h1 class="page-section-header">{{ degreeName || 'Degree Builder' }}</h1>
      </div>
      <div class="border-bottom py-3 w-50">
        <h2 class="sr-only">Requirements</h2>
        <UnitRequirements />
      </div>
      <h2 class="sr-only">Categories</h2>
      <b-container class="mt-4 mx-0 px-0" :fluid="true">
        <b-row>
          <b-col
            v-for="position in [1, 2, 3]"
            :id="`degree-template-column-${position}`"
            :key="position"
            class="degree-progress-column"
          >
            <TemplateCategoryColumn :position="position" />
          </b-col>
        </b-row>
      </b-container>
      <div v-if="config.isVueAppDebugMode" class="h-100 pt-5">
        <DebugTemplate />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DebugTemplate from '@/components/degree/DebugTemplate'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Spinner from '@/components/util/Spinner'
import store from '@/store'
import TemplateCategoryColumn from '@/components/degree/TemplateCategoryColumn'
import UnitRequirements from '@/components/degree/UnitRequirements'
import Util from '@/mixins/Util'

export default {
  name: 'DegreeTemplate',
  mixins: [Context, DegreeEditSession, Util],
  components: {
    DebugTemplate,
    Spinner,
    TemplateCategoryColumn,
    UnitRequirements
  },
  mounted() {
    const id = this.toInt(this._get(this.$route, 'params.id'))
    this.init(id).then(() => {
      if (this.sid) {
        this.$router.push(`/student/degree/${id}`)
      } else {
        this.setPageTitle(this.degreeName)
        store.dispatch('context/loadingComplete')
        this.$announcer.polite(this.templateId ? `Degree ${this.degreeName} has loaded` : 'Create degree page has loaded')
        this.putFocusNextTick('add-unit-requirement')
      }
    })
  }
}
</script>

<style scoped>
.degree-progress-column {
  min-width: 300px;
  padding-bottom: 10px;
}
</style>
