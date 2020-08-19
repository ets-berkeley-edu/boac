<template>
  <router-link
    :to="`${path}?_=${counter}&${query}`"
    @click.native="incrementCounter()">
    <slot></slot>
  </router-link>
</template>

<script>
export default {
  name: 'NavLink',
  props: {
    defaultCounter: {
      type: Number,
      required: false,
      default: 0
    },
    path: {
      type: String,
      required: true
    },
    queryArgs: {
      type: Object,
      required: false
    }
  },
  data() {
    return {
      counter: this.defaultCounter,
      query: ''
    };
  },
  created() {
    if (this.queryArgs) {
      this.$_.each(this.$_.keys(this.queryArgs), key => {
        this.query += `&${key}=${this.queryArgs[key]}`;
      });
    }
  },
  methods: {
    incrementCounter() {
      this.counter = this.counter + 1;
    }
  }
}
</script>
