<template>
  <div class="p-3">
    <Spinner />
    <div v-if="!loading">
      <div class="align-items-center d-flex pb-3">
        <div class="pr-3">
          <font-awesome :style="{color: '#3b7ea5'}" icon="plane-departure" size="2x" />
        </div>
        <div class="pt-2">
          <h1 class="page-section-header">BOA v{{ boa.version }} Flight Deck</h1>
        </div>
      </div>
      <div v-if="config.isDemoModeAvailable">
        <div class="pt-3">
          <h2 class="mb-0 page-section-header-sub">Demo Mode</h2>
        </div>
        <DemoModeToggle />
      </div>
      <div class="mt-2 pt-4">
        <h2 id="edit-service-announcement" class="page-section-header-sub">Service Alert</h2>
        <EditServiceAnnouncement />
      </div>
      <div class="mt-2 pt-5">
        <h2 id="manage-topics-header" class="page-section-header-sub">Manage Topics</h2>
        <ManageTopics />
      </div>
      <div class="mt-2 pt-5">
        <h2 class="page-section-header-sub">Alerts Log Export</h2>
        <AlertsLogExport />
      </div>
      <div class="mt-2 pt-5">
        <div class="pb-3 pt-3">
          <h2 class="mb-0 page-section-header-sub">Application Profile</h2>
        </div>
        <ul v-if="boa.build">
          <li>Artifact: {{ boa.build.artifact || '&mdash;' }}</li>
          <li v-if="boa.build.gitCommit">Git commit: <a :href="`https://github.com/ets-berkeley-edu/boac/commit/${boa.build.gitCommit}`">{{ boa.build.gitCommit }}</a></li>
        </ul>
      </div>
      <div class="pl-3">
        <div class="align-items-center d-flex">
          <div class="pb-1 pl-2">
            [<b-button
              class="m-0 p-0"
              :class="{'collapsed': showConfigs}"
              aria-controls="collapse-configs"
              variant="link"
              @click="showConfigs = !showConfigs"
            >
              <div class="pb-1">
                {{ showConfigs ? 'Hide' : 'Show' }} configs
              </div>
            </b-button>]
          </div>
        </div>
        <b-collapse id="collapse-configs" v-model="showConfigs">
          <b-table
            hover
            :items="configs"
            striped
            thead-class="sr-only"
          ></b-table>
        </b-collapse>
      </div>
    </div>
  </div>
</template>

<script>
import AlertsLogExport from '@/components/admin/AlertsLogExport'
import Context from '@/mixins/Context'
import DemoModeToggle from '@/components/admin/DemoModeToggle'
import EditServiceAnnouncement from '@/components/admin/EditServiceAnnouncement'
import ManageTopics from '@/components/topics/ManageTopics'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {getVersion} from '@/api/config'

export default {
  name: 'Admin',
  components: {
    AlertsLogExport,
    DemoModeToggle,
    EditServiceAnnouncement,
    ManageTopics,
    Spinner
  },
  mixins: [Context, Util],
  data: () => ({
    boa: undefined,
    configs: undefined,
    showConfigs: false
  }),
  mounted() {
    this.configs = []
    this._each(this.config, (value, key) => {
      this.configs.push({key, value})
    })
    getVersion().then(data => {
      this.boa = data
      this.loadingComplete('Flight Deck has loaded')
    })
  }
}
</script>
