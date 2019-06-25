<template>
  <div v-if="inDemoMode !== null">
    <h2 class="page-section-header-sub">Demo Mode</h2>
    <div class="p-2">
      <b-form-checkbox
        v-if="!isToggling"
        id="toggle-demo-mode"
        v-model="inDemoMode"
        :disabled="isToggling"
        @change="toggle">
        <span class="sr-only">Demo mode is </span>{{ inDemoMode ? 'On' : 'Off' }}
      </b-form-checkbox>
      <div v-if="isToggling" class="demo-mode-label">
        <font-awesome icon="spinner" spin />
        Toggling demo mode...
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import { setDemoMode } from '@/api/user';

export default {
  name: 'DemoModeToggle',
  mixins: [Context, UserMetadata],
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
        this.alertScreenReader(`Switching demo mode ${this.inDemoMode ? 'off' : 'on' }`);
      });
    }
  }
};
</script>

<style scoped>
.demo-mode-label {
  font-weight: 500;
  padding-bottom: 3px;
}
</style>
