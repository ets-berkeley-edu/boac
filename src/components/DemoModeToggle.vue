<template>
  <div v-if="devAuthEnabled">
    <h2>Demo Mode</h2>
    <v-switch v-model="demoMode"></v-switch>
  </div>
</template>

<script>
import store from '@/store';
import { setDemoMode } from '@/api/config';

export default {
  name: 'DemoModeToggle',
  computed: {
    devAuthEnabled() {
      return store.getters.config.devAuthEnabled;
    },
    demoMode: {
      get: () => store.getters.user,
      set: blur => setDemoMode(blur)
    }
  }
};
</script>
