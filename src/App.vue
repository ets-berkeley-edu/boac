<template>
  <div id="app" class="fill-viewport">
    <component v-bind:is="layout" v-if="layout" class="fill-viewport"></component>
  </div>
</template>

<script>
import _ from 'lodash';
import Login from './layouts/Login.vue';
import StandardLayout from './layouts/StandardLayout.vue';
import store from './store';

export default {
  name: 'App',
  computed: {
    layout: () =>
      store.getters.user
        ? _.get(store.getters.user, 'isAuthenticated')
          ? StandardLayout
          : Login
        : null
  }
};
</script>

<style scoped>
.fill-viewport {
  height: 100%;
}
</style>
