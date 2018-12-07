<template>
  <div id="app" class="fill-viewport">
    <component :is="layout"
               v-if="layout"
               class="fill-viewport"></component>
  </div>
</template>

<script>
import Login from './layouts/Login.vue';
import StandardLayout from './layouts/StandardLayout.vue';
import store from './store';

export default {
  name: 'App',
  computed: {
    layout: () =>
      store.getters.isUserAuthenticated === null
        ? null
        : store.getters.isUserAuthenticated
          ? StandardLayout
          : Login
  }
};
</script>

<style scoped>
.fill-viewport {
  height: 100%;
}
</style>
