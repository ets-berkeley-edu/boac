<template>
  <router-link
    :to="`${path}?_=${counter}`"
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
