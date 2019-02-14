<template>
  <div>
    <h2 class="page-section-header-sub pt-3">Status</h2>
    <div v-if="config">
      <h3>Config</h3>
      <div>
        <ul>
          <li>BOAC environment: {{ config.boacEnv }}</li>
          <li>Current Enrollment Term: {{ config.currentEnrollmentTerm }} ({{ config.currentEnrollmentTermId }})</li>
          <li>Disable Matrix-view Threshold: {{ config.disableMatrixViewThreshold }}</li>
          <li>Google Analytics: {{ config.googleAnalyticsId }}</li>
        </ul>
      </div>
    </div>
    <div v-if="ping">
      <h3>Ping</h3>
      <div>
        <ul>
          <li>App: {{ ping.app }}</li>
          <li>RDS: {{ ping.db }}</li>
          <li>Redshift: {{ ping.data_loch }}</li>
        </ul>
      </div>
    </div>
    <div v-if="version">
      <h3>Version</h3>
      <div>
        <ul>
          <li>Version: {{ version.version }}</li>
          <li>
            Build
            <ul>
              <li>Artifact: {{ version.build.artifact || '--' }}</li>
              <li v-if="version.build.gitCommit">Git commit: <a :href="`https://github.com/ets-berkeley-edu/boac/commit/${version.build.gitCommit}`">{{ version.build.gitCommit }}</a></li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import store from '@/store';
import { getVersion, ping } from '@/api/config';

export default {
  data: () => ({
    config: undefined,
    ping: undefined,
    version: undefined
  }),
  created() {
    store.dispatch('context/loadConfig').then(config => {
      this.config = config;
      ping().then(ping => {
        this.ping = ping;
        getVersion().then(version => {
          this.version = version;
        });
      });
    });
  }
};
</script>

<style scoped>
h3 {
  font-size: 16px;
  font-weight: 400;
  margin: 20px 0 15px 0;
  color: #999;
}
</style>
