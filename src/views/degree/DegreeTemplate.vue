<template>
  <div v-if="!loading" class="default-margins">
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
</template>

<script>
import Context from '@/mixins/Context'
import DebugTemplate from '@/components/degree/DebugTemplate'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import TemplateCategoryColumn from '@/components/degree/TemplateCategoryColumn'
import UnitRequirements from '@/components/degree/UnitRequirements'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'

export default {
  name: 'DegreeTemplate',
  components: {
    DebugTemplate,
    TemplateCategoryColumn,
    UnitRequirements
  },
  mixins: [Context, DegreeEditSession, Util],
  mounted() {
    this.loadingStart()
    const id = this.toInt(this._get(this.$route, 'params.id'))
    refreshDegreeTemplate(id).then(() => {
      if (this.sid) {
        this.$router.push(`/student/degree/${id}`)
      } else {
        this.setPageTitle(this.degreeName)
        this.loadingComplete()
        alertScreenReader(this.templateId ? `Degree ${this.degreeName} has loaded` : 'Create degree page has loaded')
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
