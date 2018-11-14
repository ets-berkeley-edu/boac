<template>
  <a v-bind:href="url">
    <slot></slot>
  </a>
</template>

<script>
import store from '@/store';

export default {
  name: 'SmartRouteRef',
  data() {
    return {
      url: null
    };
  },
  created() {
    this.url = store.state.apiBaseUrl + this.uri;
  },
  props: {
    uri: {
      type: String
    }
  }
};
</script>
