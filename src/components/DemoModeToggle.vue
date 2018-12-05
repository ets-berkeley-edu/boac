<template>
  <div class="pb-3" v-if="user.isAdmin && devAuthEnabled && inDemoMode !== null">
    <h2 class="page-section-header-sub">Demo Mode</h2>
    <div class="p-2">
      <span role="alert"
            aria-live="passive"
            class="sr-only" v-if="isToggling">Switching demo mode {{ inDemoMode ? 'off' : 'on' }}</span>
      <b-form-checkbox id="toggle-demo-mode"
                       :disabled="isToggling"
                       v-model="inDemoMode"
                       @change="toggle"
                       v-if="!isToggling">
          <span class="sr-only">Demo mode is </span>{{ inDemoMode ? 'On' : 'Off' }}
      </b-form-checkbox>
      <div class="demo-mode-label" v-if="isToggling">
        <span class="fa fa-spinner fa-spin"></span>
        Toggling demo mode...
      </div>
    </div>
  </div>
</template>

<script>
import AppConfig from '@/mixins/AppConfig';
import UserMetadata from '@/mixins/UserMetadata';
import { setDemoMode } from '@/api/config';

export default {
  name: 'DemoModeToggle',
  mixins: [AppConfig, UserMetadata],
  data: () => ({
    inDemoMode: null,
    isToggling: false
  }),
  created() {
    this.inDemoMode = this.user.inDemoMode;
  },
  methods: {
    toggle: function() {
      this.isToggling = true;
      setDemoMode(!this.inDemoMode).then(() => {
        this.inDemoMode = !this.inDemoMode;
        this.isToggling = false;
      });
    }
  }
};
</script>
