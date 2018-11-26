<template>
  <router-link :to="path"
               :params="args"
               @click.native="maybeRedirect"><slot></slot></router-link>
</template>

<script>
import _ from 'lodash';
import store from '@/store';

export default {
  name: 'SmartRef',
  computed: {
    underConstruction() {
      let route = _.get(this.$router.resolve({ path: this.path }), 'route');
      return !route || route.meta.underConstruction;
    }
  },
  methods: {
    maybeRedirect() {
      if (this.underConstruction) {
        window.location = store.state.apiBaseUrl + this.path;
      }
    }
  },
  props: {
    path: String,
    args: Object
  }
};
</script>
