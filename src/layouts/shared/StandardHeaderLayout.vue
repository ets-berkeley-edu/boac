<template>
  <v-container
    v-shortkey="['ctrl', 'alt', 's']"
    class="my-2 py-0"
    fluid
    @shortkey="() => putFocusNextTick('search-students-input')"
  >
    <v-row no-gutters>
      <v-col align-self="center" cols="auto" md="4">
        <div class="py-2">
          <HeaderBranding />
        </div>
      </v-col>
      <v-col>
        <div class="justify-center d-flex">
          <div>
            <label for="search-students-input" class="sr-only">
              {{ labelForSearchInput }}
              (Type / to put focus in the search input field.)
            </label>
            <SimpleTypeahead
              id="search-students-input"
              :key="autocompleteInputResetKey"
              aria-labelledby="search-input-label"
              class="simple-typeahead"
              :class="{
                'faint-text': !queryText,
                'search-focus-in': isFocusOnSearch || queryText,
                'search-focus-out': !isFocusOnSearch && !queryText
              }"
              :disabled="isSearching"
              :item-projection="item => item.email"
              :items="searchHistory"
              :min-input-length="1"
              name="q"
              placeholder="/ to search"
              type="search"
              @select-item="selectItem"
              @keydown.enter.prevent="search"
              @on-input="onInput"
              @on-blur="onBlur"
              @focusin="onFocusInSearch"
              @focusout="onFocusOutSearch"
            >
              <template #list-item-text="slot">
                <span v-html="slot.boldMatchText(slot.itemProjection(slot.item))"></span>
              </template>
            </SimpleTypeahead>
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
          <div v-if="currentUser.canAccessAdvisingData || currentUser.canAccessCanvasData" class="d-flex justify-center">
            <div class="pl-2">
              <v-btn
                id="go-search"
                class="btn-search"
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
                    class="px-0"
                    :class="{'border-0': !isFocusAdvSearchButton}"
                    color="white"
                    icon
                    variant="text"
                    @click.prevent="openAdvancedSearch"
                    @focusin="() => isFocusAdvSearchButton = true"
                    @focusout="() => isFocusAdvSearchButton = false"
                  >
                    <span class="sr-only">Open advanced search</span>
                    <v-icon :icon="mdiTune" size="large" />
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
import SimpleTypeahead from 'vue3-simple-typeahead'
import {mdiAlertCircle, mdiTune} from '@mdi/js'
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
    selectItem(item) {
      console.log(`search.selectItem: ${item}`)
    },
    onInput(event) {
      console.log(`search.onInput: ${event}`)
    },
    onBlur(event) {
      console.log(`search.onBlur: ${event}`)
    },
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

<style>
.search-focus-in {
  border: 0;
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

<style scoped>
.btn-search {
  background-color: transparent;
  color: white;
  font-size: 16px;
  height: 42px;
  letter-spacing: 1px;
  margin-bottom: 4px;
  margin-top: 4px;
  padding: 6px 8px;
}
.btn-search:hover {
  background-color: white;
  border-color: white;
  color: black;
}
.simple-typeahead {
  background-color: white;
  border-radius: 8px;
  border-color: rgb(238, 238, 238);
  border-style: solid;
  border-width: 1px;
  box-sizing: border-box;
  cursor: text;
  display: inline-block;
  flex-basis: 0%;
  flex-grow: 1;
  flex-shrink: 1;
  font-feature-settings: normal;
  font-kerning: auto;
  font-optical-sizing: auto;
  font-size: 16px;
  height: 50px;
  margin: 0;
  outline-offset: -2px;
  overflow-x: visible;
  overflow-y: visible;
  padding: 12px;
}
</style>
