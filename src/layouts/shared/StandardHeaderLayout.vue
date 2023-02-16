<template>
  <b-container
    v-hotkey="{'/': () => $putFocusNextTick('search-students-input')}"
    class="my-2"
    fluid
  >
    <b-row>
      <b-col align-self="center" cols="3">
        <HeaderBranding />
      </b-col>
      <b-col cols="8">
        <div class="align-items-center d-flex float-right">
          <div>
            <Autocomplete
              id="search-students-input"
              aria-labelledby="search-input-label"
              base-class="autocomplete"
              :class="{
                'faint-text': !queryText,
                'search-focus-in': isFocusOnSearch,
                'search-focus-out': !isFocusOnSearch
              }"
              :default-value="queryText"
              name="q"
              placeholder="/ to search"
              :search="onChangeAutocomplete"
              type="search"
              @keypress.enter.prevent="$_.noop"
              @submit="onSubmitAutocomplete"
              @keydown.enter="search"
              @focusin="onFocusInSearch"
              @focusout="onFocusOutSearch"
            >
              <template #result="{result, props}">
                <li v-bind="props" :id="`search-auto-suggest-${props['data-result-index']}`">
                  <span class="font-size-18">{{ result }}</span>
                </li>
              </template>
            </Autocomplete>
            <b-popover
              v-if="showErrorPopover"
              :show.sync="showErrorPopover"
              aria-live="polite"
              placement="top"
              role="alert"
              target="search-students-input"
            >
              <span id="popover-error-message" class="has-error">
                <font-awesome icon="exclamation-triangle" class="text-warning pr-1" /> Search input is required
              </span>
            </b-popover>
          </div>
          <div class="text-center">
            <label class="sr-only" for="search-options-panel-toggle">Advanced search for students, notes, appointments and classes</label>
            <b-btn
              id="search-options-panel-toggle"
              aria-controls="search-options-panel"
              variant="link"
              @click.prevent="openAdvancedSearch"
            >
              <font-awesome
                class="text-white"
                icon="sliders-h"
                size="lg"
                title="Advanced search options"
              />
            </b-btn>
            <b-popover
              placement="bottom"
              target="search-options-panel-toggle"
              triggers="hover"
              variant="primary"
            >
              Advanced search options
            </b-popover>
          </div>
          <div>
            <b-button
              id="go-search"
              class="h-100 mr-3"
              variant="outline-light"
              @keydown.enter="search"
              @click.stop="search"
            >
              Search
            </b-button>
          </div>
        </div>
        <AdvancedSearchModal :on-cancel="$_.noop" />
      </b-col>
      <b-col align-self="center" cols="1">
        <HeaderMenu class="float-right" />
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import AdvancedSearchModal from '@/components/search/AdvancedSearchModal'
import Autocomplete from '@trevoreyre/autocomplete-vue'
import Context from '@/mixins/Context'
import HeaderBranding from '@/layouts/shared/HeaderBranding'
import HeaderMenu from '@/components/header/HeaderMenu'
import Scrollable from '@/mixins/Scrollable'
import SearchSession from '@/mixins/SearchSession'
import Util from '@/mixins/Util'

export default {
  name: 'StandardHeaderLayout',
  components: {AdvancedSearchModal, Autocomplete, HeaderBranding, HeaderMenu},
  mixins: [Context, Scrollable, SearchSession, Util],
  data: () => ({
    searchHistory: [],
    showErrorPopover: false
  }),
  created() {
    this.init(this.$route.query.q).then(() => {
      document.addEventListener('keydown', this.hideError)
      document.addEventListener('click', this.hideError)
    })
  },
  methods: {
    hideError() {
      this.showErrorPopover = false
    },
    onChangeAutocomplete(input) {
      this.queryText = input
      const q = this.$_.trim(input && input.toLowerCase())
      return q.length ? this.searchHistory.filter(s => s.toLowerCase().startsWith(q)) : this.searchHistory
    },
    onFocusInSearch() {
      this.setIsFocusOnSearch(true)
      this.$announcer.polite('Search has focus')
    },
    onFocusOutSearch() {
      this.setIsFocusOnSearch(false)
    },
    onSubmitAutocomplete(value) {
      this.queryText = value
      this.search()
    },
    openAdvancedSearch() {
      this.showAdvancedSearch = true
      this.$announcer.polite('Advanced search is open')
    },
    search() {
      const q = this.$_.trim(this.queryText)
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
        this.updateSearchHistory(q)
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

<style scoped>
.search-focus-in {
  max-width: 300px;
  width: 300px;
  transition: max-width ease-out 0.2s;
}
.search-focus-out {
  max-width: 200px;
  transition: min-width ease-in 0.2s;
  width: 200px;
}
</style>
