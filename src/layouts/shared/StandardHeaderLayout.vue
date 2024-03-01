<template>
  <v-container
    v-shortkey="['ctrl', 'alt', 's']"
    class="my-2"
    fluid
    @shortkey="() => putFocusNextTick('search-students-input')"
  >
    <v-row>
      <v-col align-self="center" cols="auto" md="4">
        <div class="py-2">
          <HeaderBranding />
        </div>
      </v-col>
      <v-col>
        <div class="align-items-center d-flex">
          <div>
            <label for="search-students-input" class="sr-only">
              {{ labelForSearchInput }}
              (Type / to put focus in the search input field.)
            </label>
            <!--
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
            -->
            <v-text-field
              id="search-students-input"
              placeholder="Type here..."
            />
            <v-tooltip
              v-model="showErrorPopover"
              target="search-students-input"
              location="top"
            >
              <span
                id="popover-error-message"
                aria-live="polite"
                class="has-error"
                role="alert"
              >
                <v-icon :icon="mdiAlertCircle" class="text-warning pr-1" /> Search input is required
              </span>
            </v-tooltip>
          </div>
          <div v-if="currentUser.canAccessAdvisingData || currentUser.canAccessCanvasData" class="d-flex">
            <div class="pl-2">
              <v-btn
                id="go-search"
                class="h-100"
                variant="outlined"
                @keydown.enter="search"
                @click.stop="search"
              >
                <div class="d-flex">
                  <div v-if="isSearching" class="pr-1">
                    <v-progress-circular size="small" />
                  </div>
                  <div>
                    <span class="text-nowrap">Search<span v-if="isSearching">ing</span></span>
                  </div>
                </div>
              </v-btn>
            </div>
            <div>
              <v-tooltip location="bottom" text="Advanced search options">
                <template #activator="{}">
                  <v-btn
                    id="search-options-panel-toggle"
                    class="px-2"
                    :class="{'border-0': !isFocusAdvSearchButton}"
                    variant="text"
                    @click.prevent="openAdvancedSearch"
                    @focusin="() => isFocusAdvSearchButton = true"
                    @focusout="() => isFocusAdvSearchButton = false"
                  >
                    <span class="sr-only">Open advanced search</span>
                    <v-icon :icon="mdiTuneVariant" size="lg" />
                  </v-btn>
                </template>
              </v-tooltip>
            </div>
          </div>
        </div>
        <AdvancedSearchModal />
      </v-col>
      <v-col align-self="center" cols="auto" sm>
        <HeaderMenu class="float-right" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import {mdiAlertCircle, mdiTuneVariant} from '@mdi/js'
</script>

<script>
import AdvancedSearchModal from '@/components/search/AdvancedSearchModal'
import Context from '@/mixins/Context'
import HeaderBranding from '@/layouts/shared/HeaderBranding'
import HeaderMenu from '@/components/header/HeaderMenu'
import SearchSession from '@/mixins/SearchSession'
import Util from '@/mixins/Util'
import {addToSearchHistory, getMySearchHistory} from '@/api/search'
import {getAllTopics} from '@/api/topics'
import {scrollToTop} from '@/lib/utils'
import {useSearchStore} from '@/stores/search'

export default {
  name: 'StandardHeaderLayout',
  components: {AdvancedSearchModal, HeaderBranding, HeaderMenu},
  mixins: [Context, SearchSession, Util],
  data: () => ({
    isFocusAdvSearchButton: false,
    showErrorPopover: false
  }),
  created() {
    useSearchStore().resetAdvancedSearch(this.$route.query.q)
    getMySearchHistory().then(history => {
      useSearchStore().setSearchHistory(history)
      if (this.currentUser.canAccessAdvisingData) {
        getAllTopics(true).then(rows => {
          const topicOptions = []
          this._each(rows, row => {
            const topic = row['topic']
            topicOptions.push({
              text: topic,
              value: topic
            })
          })
          useSearchStore().setTopicOptions(topicOptions)
        })
      }
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
      this.alertScreenReader('Search has focus')
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
      this.alertScreenReader('Advanced search is open')
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
        addToSearchHistory(q).then(history => useSearchStore().setSearchHistory(history))
      } else {
        this.showErrorPopover = true
        this.alertScreenReader('Search input is required')
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
