<template>
  <div v-hotkey="{'/': () => $putFocusNextTick('search-students-input')}">
    <div class="d-flex">
      <AdvancedSearch :on-cancel="$_.noop" />
      <div>
        <div class="d-flex">
          <div class="flex-grow-1">
            <div id="search-auto-complete" class="search_field">
              <Autocomplete
                id="search-students-input"
                aria-labelledby="search-input-label"
                base-class="autocomplete"
                :class="{'faint-text': !input}"
                name="q"
                placeholder="/ to search"
                :search="onChangeAutocomplete"
                type="search"
                @keypress.enter.prevent="$_.noop"
                @submit="onSubmitAutocomplete"
              >
                <template #result="{result, props}">
                  <li v-bind="props" :id="`search-auto-suggest-${props['data-result-index']}`">
                    <span class="font-size-18">{{ result }}</span>
                  </li>
                </template>
              </Autocomplete>
            </div>
            <b-popover
              v-if="showErrorPopover"
              :show.sync="showErrorPopover"
              aria-live="polite"
              placement="top"
              role="alert"
              target="search-students-input"
            >
              <span id="popover-error-message" class="has-error"><font-awesome icon="exclamation-triangle" class="text-warning pr-1" /> Search input is required</span>
            </b-popover>
          </div>
          <div>
            <b-button
              id="go-search"
              class="h-100 ml-1 mr-0 text-white"
              variant="outline-light"
              @keypress="onSubmit"
              @click.stop="onSubmit"
            >
              Go<span class="sr-only"> (submit search)</span>
            </b-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AdvancedSearch from '@/components/search/AdvancedSearch'
import Autocomplete from '@trevoreyre/autocomplete-vue'
import Context from '@/mixins/Context'
import Scrollable from '@/mixins/Scrollable'
import Search from '@/mixins/Search'
import Util from '@/mixins/Util'
import {addToSearchHistory, getMySearchHistory} from '@/api/search'

export default {
  name: 'BasicSearch',
  components: {AdvancedSearch, Autocomplete},
  mixins: [Context, Scrollable, Search, Util],
  computed: {
    input: {
      get() {
        return this.queryText
      },
      set(value) {
        this.setQueryText(value)
      }
    }
  },
  data() {
    return {
      searchHistory: [],
      showErrorPopover: false
    }
  },
  created() {
    getMySearchHistory().then(history => {
      this.searchHistory = history
    })
    document.addEventListener('keydown', this.hideError)
    document.addEventListener('click', this.hideError)
  },
  methods: {
    hideError() {
      this.showErrorPopover = false
    },
    onChangeAutocomplete(input) {
      this.input = input
      const q = this.$_.trim(input && input.toLowerCase())
      return q.length ? this.searchHistory.filter(s => s.toLowerCase().startsWith(q)) : this.searchHistory
    },
    onSubmitAutocomplete(value) {
      const query = this.$_.trim(value || this.input)
      if (query.length) {
        this.onSubmit(query)
      }
    },
    onSubmit() {
      let el = document.getElementById('search-students-input')
      this.search(el && el.value)
    },
    search(input) {
      const q = this.$_.trim(input)
      if (q) {
        this.$router.push(
          {
            path: '/search',
            query: {
              admits: this.domain.includes('admits'),
              courses: this.domain.includes('courses'),
              notes: this.domain.includes('notes'),
              students: this.domain.includes('students'),
              q
            }
          },
          this.$_.noop
        )
        if (q) {
          addToSearchHistory(q).then(history => {
            this.searchHistory = history
          })
        }
      } else {
        this.showErrorPopover = true
        this.$announcer.polite('Search input is required')
        this.$putFocusNextTick('search-students-input')
      }
      this.scrollToTop()
    }
  }
}
</script>
