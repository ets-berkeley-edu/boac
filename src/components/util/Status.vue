<template>
  <div>
    <h2 id="system-status-header" class="page-section-header-sub pt-3">Status</h2>
    <h3>Config</h3>
    <div>
      <ul>
        <li>BOA environment: {{ $config.boacEnv }}</li>
        <li>Current Enrollment Term: {{ $config.currentEnrollmentTerm }} ({{ $config.currentEnrollmentTermId }})</li>
        <li>Disable Matrix-view Threshold: {{ $config.disableMatrixViewThreshold }}</li>
        <li>Google Analytics: {{ $config.googleAnalyticsId }}</li>
      </ul>
    </div>
    <div v-if="status">
      <h3>Ping</h3>
      <div>
        <ul>
          <li>App: {{ status.app }}</li>
          <li>RDS: {{ status.db }}</li>
          <li>Redshift: {{ status.data_loch }}</li>
        </ul>
      </div>
    </div>
    <div v-if="version">
      <h3>Version</h3>
      <div>
        <ul>
          <li>Version: {{ version.version }}</li>
          <li v-if="version.build">
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
import { getVersion, ping } from '@/api/config';

export default {
  data: () => ({
    status: undefined,
    version: undefined
  }),
  created() {
    ping().then(status => {
      this.status = status;
      getVersion().then(version => {
        this.version = version;
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
