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
    </div>
    <div v-if="$config.isVueAppDebugMode" class="pt-5">
      <div class="align-items-center d-flex">
        <div class="pb-1 pl-2">
          <b-button
            class="m-0 p-0"
            :class="{'collapsed': showDebug}"
            aria-controls="collapse-degree-edit-debug"
            variant="link"
            @click="showDebug = !showDebug"
          >
            <div class="pb-1">
              <font-awesome :icon="showDebug ? 'caret-down' : 'caret-right'" :class="showDebug ? 'mr-1' : 'ml-1 mr-1'" />
              {{ showDebug ? 'Hide' : 'Show' }} degree-edit debug
            </div>
          </b-button>
        </div>
      </div>
      <b-collapse id="collapse-degree-edit-debug" v-model="showDebug">
        <div class="align-items-center d-flex py-2">
          <div class="font-weight-500 pb-1 pr-2">Degree_Edit_Session</div>
          <div v-if="disableButtons">
            <b-btn
              class="mb-1 px-0"
              variant="link"
              @click="setDisableButtons(false)"
            >
              Force enable buttons
            </b-btn>
          </div>
        </div>
        <div>
          <pre>{{ degreeEditSessionToString }}</pre>
        </div>
      </b-collapse>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import TemplateCategoryColumn from '@/components/degree/TemplateCategoryColumn'
import UnitRequirements from '@/components/degree/UnitRequirements'
import Util from '@/mixins/Util'

export default {
  name: 'DegreeTemplate',
  components: {
    TemplateCategoryColumn,
    Spinner,
    UnitRequirements
  },
  mixins: [Context, DegreeEditSession, Loading, Util],
  data: () => ({
    showDebug: false
  }),
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
