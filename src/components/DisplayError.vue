<template>
  <div v-if="errors.length">
    <ul>
      <li class="has-error" v-for="error in errors" v-bind:key="error.id">
        {{error}} [<button v-on:click="dismissError(error.id)">dismiss</button>
      </li>
    </ul>
  </div>
</template>

<script>
import store from '@/store';

export default {
  name: 'DisplayError',
  data() {
    return {
      errors: store.getters['context/errors']
    };
  },
  methods: {
    dismissError(id) {
      store.dispatch('context/dismissError', id);
    }
  }
};
</script>
