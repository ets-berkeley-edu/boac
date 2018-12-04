<template>
  <div>
    <h2 class="page-section-header-sub">Demo Mode</h2>
    <div class="demo-mode-switch-container" v-if="devAuthEnabled && inDemoMode !== null">
      <b-form-checkbox id="toggle-demo-mode"
                       :disabled="isToggling"
                       @change="toggle"
                       v-if="!isToggling">
          {{inDemoMode ? 'On' : 'Off'}}
      </b-form-checkbox>
      <label class="sr-only" for="toggle-demo-mode">Demo mode is </label>
      <div class="demo-mode-label" v-if="isToggling">
        <span class="fa fa-spinner fa-spin"></span>
        Toggling demo mode...
      </div>
    </div>
  </div>
</template>

<script>
import { setDemoMode } from '@/api/config';
import AppConfig from '@/mixins/AppConfig';
import UserMetadata from '@/mixins/UserMetadata';

export default {
  name: 'DemoModeToggle',
  mixins: [AppConfig, UserMetadata],
  data: () => ({
    isToggling: false
  }),
  methods: {
    toggle: function() {
      this.isToggling = true;
      setDemoMode(!this.inDemoMode).then(() => {
        this.isToggling = false;
      });
    }
  }
};
</script>
