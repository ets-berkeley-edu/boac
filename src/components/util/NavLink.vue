<template>
  <router-link
    :to="`${path}?_=${counter}&${query}`"
    @click.native="incrementCounter()">
    <slot></slot>
  </router-link>
</template>

<script>
export default {
  name: "NavLink",
  props: {
    path: {
      type: String,
      required: true
    },
    queryArgs: {
      type: Object,
      required: false
    }
  },
  data: () => ({
    counter: 0,
    query: ''
  }),
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
