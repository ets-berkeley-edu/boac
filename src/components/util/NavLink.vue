<template>
  <router-link :to="{path, query}" @click="() => counter++">
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
      default: undefined,
      required: false,
      type: Object
    }
  },
  data: () => ({
    counter: undefined
  }),
  computed: {
    query() {
      const args = this.queryArgs || {}
      return {
        ...{'_': this.counter},
        ...args
      }
    }
  },
  created() {
    this.counter = this.defaultCounter
  }
}
</script>
