<template>
  <div>
    <h2 class="page-section-header-sub">Demo Mode</h2>
    <div class="demo-mode-switch-container" v-if="devAuthEnabled && inDemoMode !== null">
      <label class="switch" v-if="!isToggling">
        <input id="toggle-demo-mode"
               type="checkbox"
               v-bind:class="{'demo-mode-input-checked': inDemoMode}"
               :disabled="isToggling"
               v-model="inDemoMode"
               v-on:click="toggle"
               :value="inDemoMode ? 'on' : 'off'"/>
        <span class="slider round"></span>
      </label>
      <label class="sr-only" for="toggle-demo-mode">Demo mode</label>
      <div class="demo-mode-label" v-if="isToggling">
        <span class="fa fa-spinner fa-spin"></span>
        Toggling demo mode...
      </div>
      <div class="demo-mode-label" v-if="!isToggling">
        {{inDemoMode ? 'On' : 'Off'}}
      </div>
    </div>
  </div>
</template>

<script>
import store from '@/store';
import { setDemoMode } from '@/api/config';

export default {
  name: 'DemoModeToggle',
  data: () => ({
    inDemoMode: null,
    isToggling: false
  }),
  created() {
    this.inDemoMode = store.getters.user.inDemoMode;
  },
  computed: {
    devAuthEnabled() {
      return store.getters.config.devAuthEnabled;
    }
  },
  methods: {
    toggle: function() {
      this.isToggling = true;
      this.inDemoMode = !this.inDemoMode;
      setDemoMode(this.inDemoMode).then(() => {
        this.isToggling = false;
      });
    }
  }
};
</script>
