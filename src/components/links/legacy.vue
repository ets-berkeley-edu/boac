<template>
  <a v-bind:href="url">
    <slot></slot>
  </a>
</template>

<script>
import store from '@/store';

export default {
  name: 'LegacyLink',
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
