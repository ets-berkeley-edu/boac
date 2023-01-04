<template>
  <Autocomplete
    :id="id"
    :aria-labelledby="ariaLabelledby"
    :aria-required="required"
    :base-class="disabled ? 'disabled' : 'autocomplete'"
    :class="{'faint-text': !input}"
    :disabled="disabled"
    :placeholder="placeholder"
    :search="search"
    :type="type"
    @keypress.enter.prevent="$_.noop"
    @submit="handleSubmit"
  />
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
    disabled: {
      required: false,
      type: Boolean
    },
    getSuggestions: {
      required: true,
      type: Function
    },
    id: {
      required: true,
      type: String
    },
    onSubmit: {
      required: true,
      type: Function
    },
    placeholder: {
      required: false,
      type: String
    },
    required: {
      required: false,
      type: Boolean
    },
    type: {
      default: 'input',
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
  box-sizing: border-box;
  color: #333;
  font-size: 16px;
  height: 45px;
  padding: 0 10px 0 10px;
  width: 100%;
}
.autocomplete-result {
  padding: 12px;
  background-image: none;
  background-position: 12px;
}
.disabled-input {
  background-color: #ddd;
  background-image: none;
  border: 2px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
  color: #333;
  font-size: 16px;
  height: 45px;
  padding: 0 10px 0 10px;
  width: 100%;
}
</style>
