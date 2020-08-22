<template>
  <div :id="id">
    <b-input-group>
      <b-form-input
        :id="`${id}-input`"
        ref="autocompleteInput"
        v-model="query"
        :aria-readonly="disabled"
        :class="inputClass"
        :disabled="disabled"
        :placeholder="placeholder"
        :maxlength="maxlength"
        name="autocomplete-name"
        :required="isRequired"
        :type="demoModeBlur && $currentUser.inDemoMode ? 'password' : 'text'"
        autocomplete="off"
        @input="onTextInput"
        @focusin="makeSuggestions"
        @keypress.enter.prevent="onEnter"
        @keyup.esc="onEscInput"
        @keyup.down="onArrowDown">
      </b-form-input>
      <b-input-group-append v-if="showAddButton">
        <b-button
          :id="`${id}-add-button`"
          class="btn btn-primary-color-override"
          :disabled="!selectedSuggestion || addButtonLoading"
          @click="addSuggestion"
          @keyup.enter="addSuggestion">
          <div v-if="!addButtonLoading">
            <font-awesome icon="plus" /> Add
          </div>
          <div v-if="addButtonLoading">
            <font-awesome icon="spinner" spin />
          </div>
        </b-button>
      </b-input-group-append>
    </b-input-group>
    <div v-if="restrict || suggestions.length" class="dropdown">
      <ul
        :id="`${id}-suggestions`"
        ref="autocompleteSuggestions"
        :class="isOpen ? `d-block ${dropdownClass}` : dropdownClass"
        aria-expanded="true"
        class="dropdown-menu"
        role="menu"
        tabIndex="0"
        @keyup.down="onArrowDown"
        @keyup.up="onArrowUp"
        @keyup.esc="onEsc">
        <li
          v-if="isLoading"
          class="dropdown-item">
          <font-awesome icon="spinner" spin />
        </li>
        <li
          v-if="restrict && !isLoading && !suggestions.length"
          :id="`${id}-no-results`"
          class="dropdown-item">
          No results.
        </li>
        <li
          v-for="(suggestion, i) in suggestions"
          :key="i">
          <a
            :id="`${id}-suggestion-${i}`"
            :class="{'demo-mode-blur': demoModeBlur && $currentUser.inDemoMode}"
            role="menuitem"
            class="dropdown-item"
            tabindex="0"
            @click="selectSuggestion(suggestion)"
            @keyup.enter="selectSuggestion(suggestion)">
            <span :class="suggestionLabelClass" v-html="highlightQuery(suggestion)"></span>
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import Util from '@/mixins/Util';

export default {
  name: 'Autocomplete',
  mixins: [Util],
  props: {
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
    id: {
      required: true,
      type: String
    },
    isRequired: {
      required: false,
      type: Boolean
    },
    inputClass: {
      default: '',
      required: false,
      type: String
    },
    onAddButton: {
      default: () => {},
      required: false,
      type: Function
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
      default: true,
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
      onTextInput: this.debounce(this.makeSuggestions, 200),
      selectedSuggestion: false,
      suggestions: [],
      suggestionElements: [],
      suggestionFocusIndex: null
    };
  },
  watch: {
    disabled(isDisabled) {
      if (isDisabled) {
        this.closeSuggestions();
      }
    }
  },
  mounted() {
    document.addEventListener('click', this.onClickOutside)
  },
  destroyed() {
    document.removeEventListener('click', this.onClickOutside)
  },
  methods: {
    addSuggestion() {
      this.addButtonLoading = true;
      this.onAddButton(this.selectedSuggestion).then(() => {
        this.addButtonLoading = false;
        this.closeSuggestions();
      });
    },
    closeSuggestions() {
      this.isOpen = false;
      this.$nextTick(() => {
        if (!this.value) {
          this.query = null;
        }
      });
    },
    getQuery() {
      return this.query;
    },
    highlightQuery(suggestion) {
      if (suggestion && suggestion.label) {
        const regex = new RegExp(this.escapeForRegExp(this.query), 'i');
        const match = suggestion.label.match(regex);
        if (!match) {
          return suggestion.label;
        }
        const matchedText = suggestion.label.substring(match.index, match.index + match[0].toString().length);
        return suggestion.label.replace(regex, `<strong>${matchedText}</strong>`);
      }
    },
    makeSuggestions() {
      this.selectedSuggestion = null;
      this.$emit('input', null);
      if (this.suggestWhen(this.query)) {
        this.isOpen = true;
        this.isLoading = true;
        this.suggestions = [];
        const q = this.query && this.escapeForRegExp(this.query).replace(/[^\w ]+/g, '');
        this.source(q, this.limit).then(results => {
          this.populateSuggestions(results);
        });
      } else {
        this.isOpen = false;
      }
    },
    onArrowDown() {
      if (this.suggestionElements.length) {
        if (this.suggestionFocusIndex === null) {
          this.suggestionFocusIndex = 0;
          this.suggestionElements[this.suggestionFocusIndex].focus();
        } else if (this.suggestionFocusIndex + 1 < this.suggestionElements.length) {
          this.suggestionFocusIndex++;
          this.suggestionElements[this.suggestionFocusIndex].focus();
        }
      }
    },
    onArrowUp() {
      if (this.suggestionElements.length) {
        if (this.suggestionFocusIndex === 0) {
          this.suggestionFocusIndex = null;
          this.$refs.autocompleteInput.$el.focus();
        } else if (this.suggestionFocusIndex) {
          this.suggestionFocusIndex--;
          this.suggestionElements[this.suggestionFocusIndex].focus();
        }
      }
    },
    onClickOutside(evt) {
      if (!this.$el.contains(evt.target)) {
        if (this.restrict) {
          // Close suggestions and clear the input.
          this.closeSuggestions();
        } else {
          // Close only.
          this.isOpen = false;
        }
      }
    },
    onEnter() {
      if (this.restrict) {
        this.onArrowDown();
      } else {
        this.selectSuggestion({ label: this.query });
      }
    },
    onEsc() {
      this.closeSuggestions();
    },
    onEscInput() {
      if (this.onEscFormInput) {
        this.onEscFormInput();
      } else {
        this.closeSuggestions();
      }
    },
    populateSuggestions(results) {
      this.suggestions = results;
      this.isLoading = false;
      this.isOpen = true;
      this.suggestionFocusIndex = null;
      this.$nextTick(() => {
        const el = this.$refs.autocompleteSuggestions;
        this.suggestionElements = el ? el.querySelectorAll('.dropdown-item') : [];
      });
    },
    selectSuggestion(suggestion) {
      this.isOpen = false;
      this.query = suggestion.label;
      this.selectedSuggestion = suggestion;
      this.$emit('input', suggestion);
    }
  }
};
</script>

<style scoped>
.dropdown {
  z-index: 100;
}
.dropdown-item {
  cursor: pointer;
}
</style>
