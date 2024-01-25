<template>
  <b-container
    v-hotkey="{'/': () => putFocusNextTick('search-students-input')}"
    class="my-2"
    fluid
  >
    <b-row>
      <b-col align-self="center" cols="auto" md="4">
        <div class="py-2">
          <HeaderBranding />
        </div>
      </b-col>
      <b-col>
        <div class="align-items-center d-flex">
          <div>
            <label for="search-students-input" class="sr-only">
              {{ labelForSearchInput }}
              (Type / to put focus in the search input field.)
            </label>
            <Autocomplete
              id="search-students-input"
              :key="autocompleteInputResetKey"
              aria-labelledby="search-input-label"
              base-class="autocomplete"
              :class="{
                'faint-text': !queryText,
                'search-focus-in': isFocusOnSearch || queryText,
                'search-focus-out': !isFocusOnSearch && !queryText
              }"
              :default-value="queryText"
              :disabled="isSearching"
              name="q"
              placeholder="/ to search"
              :search="onChangeAutocomplete"
              type="search"
              @keydown.enter.prevent="search"
              @submit="onSubmitAutocomplete"
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
          <div v-if="currentUser.canAccessAdvisingData || currentUser.canAccessCanvasData" class="d-flex">
            <div class="pl-2">
              <b-btn
                id="go-search"
                class="h-100"
                variant="outline-light"
                @keydown.enter="search"
                @click.stop="search"
              >
                <div class="d-flex">
                  <div v-if="isSearching" class="pr-1">
                    <b-spinner small />
                  </div>
                  <div>
                    <span class="text-nowrap">Search<span v-if="isSearching">ing</span></span>
                  </div>
                </div>
              </b-btn>
            </div>
            <div>
              <b-btn
                id="search-options-panel-toggle"
                class="px-2"
                :class="{'border-0': !isFocusAdvSearchButton}"
                variant="outline-light"
                @click.prevent="openAdvancedSearch"
                @focusin="() => isFocusAdvSearchButton = true"
                @focusout="() => isFocusAdvSearchButton = false"
              >
                <span class="sr-only">Open advanced search</span>
                <font-awesome
                  icon="sliders-h"
                  size="lg"
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
          </div>
        </div>
        <AdvancedSearchModal />
      </b-col>
      <b-col align-self="center" cols="auto" sm>
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
import SearchSession from '@/mixins/SearchSession'
import Util from '@/mixins/Util'
import {scrollToTop} from '@/utils'

export default {
  name: 'StandardHeaderLayout',
  components: {AdvancedSearchModal, Autocomplete, HeaderBranding, HeaderMenu},
  mixins: [Context, SearchSession, Util],
  data: () => ({
    isFocusAdvSearchButton: false,
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
      const q = this._trim(input && input.toLowerCase())
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
      const q = this._trim(this.queryText)
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
          this._noop
        )
        this.updateSearchHistory(q)
      } else {
        this.showErrorPopover = true
        this.$announcer.polite('Search input is required')
        this.putFocusNextTick('search-students-input')
      }
      scrollToTop()
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
