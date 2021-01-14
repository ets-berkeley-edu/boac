<template>
  <Autocomplete
    :aria-labelledby="ariaLabelledby"
    :placeholder="placeholder"
    :search="search"
    @submit="handleSubmit"
  ></Autocomplete>
</template>

<script>
import Autocomplete from '@trevoreyre/autocomplete-vue'
import '@trevoreyre/autocomplete-vue/dist/style.css'

export default {
  name: 'InputAutocomplete',
  components: {Autocomplete},
  props: {
    ariaLabelledby: {
      required: true,
      type: String
    },
    getSuggestions: {
      required: true,
      type: Function
    },
    onSubmit: {
      required: true,
      type: Function
    },
    placeholder: {
      required: false,
      type: String
    }
  },
  data: () => ({
    input: undefined
  }),
  methods: {
    handleSubmit(value) {
      const q = this.$_.trim(value || this.input)
      if (q.length) {
        this.onSubmit(value || this.input)
      }
    },
    search(input) {
      this.input = input
      return this.getSuggestions(input)
    }
  }
}
</script>

<style>
.autocomplete-input {
  background-color: #fff;
  background-image: none;
  border: 2px solid #ccc;
  border-radius: 4px;
  color: #333;
  height: 45px;
  padding: 0 10px 0 10px;
}
.autocomplete-result {
	padding: 12px;
	background-image: none;
	background-position: 12px;
}
</style>
