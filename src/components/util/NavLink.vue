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
    query: {
      default: '',
      type: String,
      required: false
    }
  },
  data: () => ({
    counter: 0
  }),
  methods: {
    incrementCounter() {
      this.counter = this.counter + 1;
    }
  }
}
</script>
