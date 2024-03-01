<template>
  <div :id="id">
    <b-input-group>
      <v-text-field
        :id="`${id}-input`"
        ref="autocompleteInput"
        v-model="query"
        :aria-labelledby="inputLabelledBy"
        :aria-readonly="disabled"
        autocomplete="off"
        :class="inputClass"
        :disabled="disabled"
        :maxlength="maxlength"
        name="autocomplete-name"
        :placeholder="placeholder"
        :type="demoModeBlur && currentUser.inDemoMode ? 'password' : formInputType"
        @focusin="makeSuggestions"
        @input="onTextInput"
        @keypress.enter.prevent="onEnter"
        @keyup.esc="onEscInput"
        @keyup.down="onArrowDown"
      />
      <slot name="append"></slot>
      <b-input-group-append v-if="showAddButton">
        <v-btn
          :id="`${id}-add-button`"
          class="btn btn-primary-color-override"
          :disabled="addButtonLoading || isLoading || (!selectedSuggestion && !(fallback && fallbackWhen(query)))"
          @click="onAddButton"
          @keyup.enter="onAddButton"
        >
          <div v-if="!addButtonLoading">
            <v-icon :icon="mdiPlus" /> Add
          </div>
          <div v-if="addButtonLoading">
            <v-progress-circular size="small" />
          </div>
        </v-btn>
      </b-input-group-append>
    </b-input-group>
    <div v-if="restrict || suggestions.length" class="dropdown">
      <ul
        :id="`${id}-suggestions`"
        ref="autocompleteSuggestions"
        :class="isOpen ? `d-block ${dropdownClass}` : dropdownClass"
        aria-expanded="true"
        class="dropdown-menu"
        @keyup.down="onArrowDown"
        @keyup.up="onArrowUp"
        @keyup.esc="onEsc"
      >
        <li
          v-if="isLoading"
          class="dropdown-item"
        >
          <v-progress-circular size="small" />
        </li>
        <li
          v-if="restrict && !isLoading && !suggestions.length"
          :id="`${id}-no-results`"
          class="dropdown-item"
        >
          No results.
        </li>
        <li v-for="(suggestion, index) in suggestions" :key="index" role="menuitem">
          <a
            :id="`${id}-suggestion-${index}`"
            :aria-label="getAriaLabelForSuggestion(index)"
            :class="{'demo-mode-blur': demoModeBlur && currentUser.inDemoMode}"
            role="menuitem"
            class="dropdown-item"
            tabindex="0"
            @click="selectSuggestion(suggestion)"
            @keyup.enter="selectSuggestion(suggestion)"
          >
            <span :class="suggestionLabelClass" v-html="highlightQuery(suggestion)"></span>
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {mdiPlus} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'

export default {
  name: 'InputTextAutocomplete',
  mixins: [Context, Util],
  props: {
    addSelection: {
      default: () => {},
      required: false,
      type: Function
    },
    demoModeBlur: {
      required: false,
      type: Boolean
    },
    disabled: {
      required: false,
      type: Boolean
    },
    dropdownClass: {
      default: '',
      required: false,
      type: String
    },
    fallback: {
      default: () => {},
      required: false,
      type: Function
    },
    fallbackWhen: {
      default: () => {},
      required: false,
      type: Function
    },
    formInputType: {
      default: 'text',
      required: false,
      type: String
    },
    id: {
      required: true,
      type: String
    },
    inputClass: {
      default: '',
      required: false,
      type: String
    },
    inputLabelledBy: {
      required: true,
      type: String
    },
    onEscFormInput: {
      default: () => {},
      required: false,
      type: Function
    },
    maxlength: {
      default: '56',
      required: false,
      type: String
    },
    placeholder: {
      default: undefined,
      required: false,
      type: String
    },
    restrict: {
      default: true, // eslint-disable-line vue/no-boolean-default
      required: false,
      type: Boolean
    },
    showAddButton: {
      required: false,
      type: Boolean
    },
    source: {
      required: true,
      type: Function
    },
    suggestionLabelClass: {
      default: '',
      required: false,
      type: String
    },
    suggestWhen: {
      default: query => query && query.length > 1,
      required: false,
      type: Function
    },
    value: {
      default: undefined,
      required: false,
      type: Object
    }
  },
  data() {
    return {
      addButtonLoading: false,
      isOpen: false,
      isLoading: false,
      limit: 20,
      query: null,
      onTextInput: this._debounce(this.makeSuggestions, 200),
      selectedSuggestion: false,
      suggestions: [],
      suggestionElements: [],
      suggestionFocusIndex: null
    }
  },
  watch: {
    disabled(isDisabled) {
      if (isDisabled) {
        this.closeSuggestions()
      }
    }
  },
  mounted() {
    document.addEventListener('click', this.onClickOutside)
  },
  unmounted() {
    document.removeEventListener('click', this.onClickOutside)
  },
  methods: {
    closeSuggestions() {
      if (this.isOpen) {
        this.alertScreenReader('Closing auto-suggest dropdown')
      }
      this.isOpen = false
      this.nextTick(() => {
        if (!this.value) {
          this.query = null
        }
      })
    },
    getAriaLabelForSuggestion(index) {
      return (index === 0 ? `You have ${this.suggestions.length} auto-suggestion${this.suggestions.length === 1 ? '' : 's'}. ` : '') + `Hit enter to search '${this.suggestions[index].label}'`
    },
    getQuery() {
      return this.query
    },
    highlightQuery(suggestion) {
      if (suggestion && suggestion.label) {
        const regex = new RegExp(this.escapeForRegExp(this.query), 'i')
        const match = suggestion.label.match(regex)
        if (!match) {
          return suggestion.label
        }
        const matchedText = suggestion.label.substring(match.index, match.index + match[0].toString().length)
        return suggestion.label.replace(regex, `<strong>${matchedText}</strong>`)
      }
    },
    makeSuggestions() {
      this.selectedSuggestion = null
      this.$emit('input', null)
      if (this.suggestWhen(this.query)) {
        this.isOpen = true
        this.isLoading = true
        this.suggestions = []
        const q = this.query && this.escapeForRegExp(this.query).replace(/[^\w ]+/g, '')
        this.source(q, this.limit).then(results => {
          if (this.suggestWhen(this.query)) {
            this.populateSuggestions(results)
          } else {
            this.isLoading = false
          }
        })
      } else {
        this.isOpen = false
      }
    },
    onAddButton() {
      this.addButtonLoading = true
      const handler = (this.fallback && this.fallbackWhen(this.query)) ? this.fallback : this.addSelection
      handler(this.selectedSuggestion || this.query).then(() => {
        this.closeSuggestions()
      }).catch(() => {
        this.nextTick(() => this.isOpen = false)
      }).finally(() => {
        this.addButtonLoading = false
      })
    },
    onArrowDown() {
      if (this.suggestionElements.length) {
        if (this.suggestionFocusIndex === null) {
          this.suggestionFocusIndex = 0
          this.suggestionElements[this.suggestionFocusIndex].focus()
        } else if (this.suggestionFocusIndex + 1 < this.suggestionElements.length) {
          this.suggestionFocusIndex++
          this.suggestionElements[this.suggestionFocusIndex].focus()
        }
      }
    },
    onArrowUp() {
      if (this.suggestionElements.length) {
        if (this.suggestionFocusIndex === 0) {
          this.suggestionFocusIndex = null
          this.$refs.autocompleteInput.$el.focus()
        } else if (this.suggestionFocusIndex) {
          this.suggestionFocusIndex--
          this.suggestionElements[this.suggestionFocusIndex].focus()
        }
      }
    },
    onClickOutside(evt) {
      if (!this.$el.contains(evt.target)) {
        if (this.restrict) {
          // Close suggestions and clear the input.
          this.closeSuggestions()
        } else {
          // Close only.
          this.isOpen = false
        }
      }
    },
    onEnter() {
      if (this.restrict) {
        this.onArrowDown()
      } else {
        this.selectSuggestion({label: this.query})
      }
    },
    onEsc() {
      this.closeSuggestions()
    },
    onEscInput() {
      if (this.onEscFormInput) {
        this.onEscFormInput()
      } else {
        this.closeSuggestions()
      }
    },
    populateSuggestions(results) {
      this.suggestions = results
      this.isLoading = false
      this.isOpen = true
      this.suggestionFocusIndex = null
      this.nextTick(() => {
        const el = this.$refs.autocompleteSuggestions
        this.suggestionElements = el ? el.querySelectorAll('.dropdown-item') : []
      })
    },
    selectSuggestion(suggestion) {
      this.isOpen = false
      this.query = suggestion.label
      this.selectedSuggestion = suggestion
      this.$emit('input', suggestion)
    }
  }
}
</script>

<style scoped>
.dropdown {
  z-index: 100;
}
.dropdown-item {
  cursor: pointer;
}
</style>
