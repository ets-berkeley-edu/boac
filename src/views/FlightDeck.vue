<template>
  <div class="p-3">
    <Spinner alert-prefix="The Admin page" />
    <div v-if="!loading">
      <div class="align-items-center d-flex pb-3">
        <div class="pr-3">
          <font-awesome :style="{color: '#3b7ea5'}" icon="plane-departure" size="2x" />
        </div>
        <div class="pt-2">
          <h1 class="page-section-header">BOA v{{ boa.version }} Flight Deck</h1>
        </div>
      </div>
      <div v-if="dropInSchedulingDepartments.length">
        <DropInSchedulerManagement
          v-for="dept in dropInSchedulingDepartments"
          :key="dept.code"
          :dept="dept" />
      </div>
      <div v-if="$config.isDemoModeAvailable">
        <div class="pt-3">
          <h2 class="mb-0 page-section-header-sub">Demo Mode</h2>
        </div>
        <DemoModeToggle />
      </div>
      <div>
        <EditServiceAnnouncement />
      </div>
      <div v-if="boa.version.build">
        <h3>Build</h3>
        <div>Artifact: {{ boa.version.build.artifact || '&mdash;' }}</div>
        <div v-if="boa.version.build.gitCommit">Git commit: <a :href="`https://github.com/ets-berkeley-edu/boac/commit/${boa.version.build.gitCommit}`">{{ boa.version.build.gitCommit }}</a></div>
      </div>
      <div class="pt-4">
        <div class="align-items-center d-flex">
          <div>
            <h3 id="system-status-header" class="page-section-header-sub">Application Configs</h3>
          </div>
          <div class="pb-1 pl-2">
            [<b-button
              class="m-0 p-0"
              :class="{'collapsed': showConfigs}"
              :aria-expanded="showConfigs"
              aria-controls="collapse-configs"
              variant="link"
              @click="showConfigs = !showConfigs">
              <div class="pb-1">
                {{ showConfigs ? 'hide' : 'show' }}
              </div>
            </b-button>]
          </div>
        </div>
        <b-collapse id="collapse-configs" v-model="showConfigs">
          <b-table
            hover
            :items="configs"
            striped
            thead-class="sr-only"></b-table>
        </b-collapse>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import DemoModeToggle from '@/components/admin/DemoModeToggle';
import DropInSchedulerManagement from '@/components/admin/DropInSchedulerManagement';
import EditServiceAnnouncement from '@/components/admin/EditServiceAnnouncement';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import Util from '@/mixins/Util';
import { getVersion } from '@/api/config';
import { getDropInSchedulers } from '@/api/user';

export default {
  name: 'Admin',
  components: {
    DropInSchedulerManagement,
    DemoModeToggle,
    EditServiceAnnouncement,
    Spinner
  },
  mixins: [Context, Loading, Util],
  data: () => ({
    boa: undefined,
    configs: undefined,
    dropInSchedulingDepartments: [],
    showConfigs: false
  }),
  mounted() {
    this.configs = []
    this.$_.each(this.$config, (value, key) => {
      this.configs.push({key, value})
    });
    getDropInSchedulers().then(departments => {
      this.dropInSchedulingDepartments = departments;
      getVersion().then(data => {
        this.boa = data;
        this.loaded('Flight Deck');
      });
    });
  }
};
</script>
