<template>
  <router-link :to="{path, query}" @click.native="() => counter++">
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
  data: () => ({
    counter: undefined
  }),
  computed: {
    query() {
      return {
        ...{'_': this.counter},
        ...this.queryArgs
      }
    }
  },
  created() {
    this.counter = this.defaultCounter
  }
}
</script>
