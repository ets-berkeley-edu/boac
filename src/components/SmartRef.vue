<template>
  <router-link :to="path"
               @click.native="maybeRedirect"><slot></slot></router-link>
</template>

<script>
import _ from 'lodash';
import store from '@/store';

export default {
  name: 'SmartRef',
  computed: {
    legacyUri() {
      let route = _.get(this.$router.resolve({ path: this.path }), 'route');
      return !route || _.get(route, 'meta.legacyUri');
    }
  },
  methods: {
    maybeRedirect() {
      if (this.legacyUri) {
        let uri = this.objectId
          ? _.replace(this.legacyUri, ':id', this.objectId)
          : this.legacyUri;
        window.location = store.state.apiBaseUrl + uri;
      }
    }
  },
  props: {
    path: String,
    objectId: Number
  }
};
</script>
