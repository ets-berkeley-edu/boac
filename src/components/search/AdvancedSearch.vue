<template>
  <div class="justify-center d-flex">
    <div class="align-center d-flex">
      <div class="mr-2">
        <label for="search-students-input" class="sr-only">
          {{ labelForSearchInput }}
          (Type / to put focus in the search input field.)
        </label>
        <v-combobox
          id="search-students-input"
          :key="autocompleteInputResetKey"
          v-model="queryText"
          aria-labelledby="search-input-label"
          bg-color="white"
          :class="{
            'faint-text': !queryText,
            'search-focus-in': isFocusOnSearch || queryText,
            'search-focus-out': !isFocusOnSearch && !queryText
          }"
          density="comfortable"
          :disabled="isSearching"
          hide-details
          hide-no-data
          :items="useSearchStore().searchHistory"
          :menu-icon="null"
          placeholder="/ to search"
          type="search"
          variant="outlined"
          @focusin="() => useSearchStore().setIsFocusOnSearch(true)"
          @focusout="() => useSearchStore().setIsFocusOnSearch(false)"
          @keydown.enter.prevent="search"
        >
          <template #append-inner>
            <v-btn
              v-if="!isSearching && size(trim(queryText))"
              aria-label="Clear search input"
              icon
              size="x-small"
              @click="() => queryText = null"
            >
              <v-icon :icon="mdiClose" />
            </v-btn>
            <v-progress-circular
              v-if="isSearching"
              indeterminate
              size="x-small"
              width="2"
            />
          </template>
        </v-combobox>
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
      <v-btn
        v-if="currentUser.canAccessAdvisingData || currentUser.canAccessCanvasData"
        id="go-search"
        class="btn-search"
        text="Search"
        variant="outlined"
        @keydown.enter="search"
        @click.stop="search"
      />
      <AdvancedSearchModal v-if="currentUser.canAccessAdvisingData || currentUser.canAccessCanvasData" />
    </div>
  </div>
</template>

<script setup>
import AdvancedSearchModal from '@/components/search/AdvancedSearchModal'
import {mdiAlertCircle, mdiClose} from '@mdi/js'
import {size} from 'lodash'
</script>

<script>
import Context from '@/mixins/Context'
import SearchSession from '@/mixins/SearchSession'
import {addToSearchHistory, getMySearchHistory} from '@/api/search'
import {getAllTopics} from '@/api/topics'
import {useSearchStore} from '@/stores/search'
import {scrollToTop} from '@/lib/utils'
import {each, noop, trim} from 'lodash'

export default {
  name: 'StandardHeaderLayout',
  mixins: [Context, SearchSession],
  data: () => ({
    showErrorPopover: false
  }),
  created() {
    useSearchStore().resetAdvancedSearch(this.$route.query.q)
    getMySearchHistory().then(history => {
      useSearchStore().setSearchHistory(history)
      if (this.currentUser.canAccessAdvisingData) {
        getAllTopics(true).then(rows => {
          const topicOptions = [{text: 'Any topic', value: null}]
          each(rows, row => {
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
    search() {
      const q = trim(this.queryText)
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
          noop
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
.btn-search {
  background-color: transparent;
  color: white;
  font-size: 16px;
  height: 46px;
  letter-spacing: 1px;
  padding: 6px 8px;
}
.btn-search:hover {
  background-color: white;
  border-color: white;
  color: #3b7ea5;
}
/*
.simple-typeahead {
  display: inline-block;
  onClickClearflex-basis: 0%;
  onClickClearflex-grow: 1;
  onClickClearflex-shrink: 1;
  onClickClearfont-feature-settings: normal;
  onClickClearfont-kerning: auto;
  onClickClearfont-optical-sizing: auto;
  onClickClearfont-size: 16px;
  onClickClearheight: 50px;
  onClickClearmargin: 0;
  onClickClearoutline-offset: -2px;
  onClickClearoverflow-x: visible;
  onClickClearoverflow-y: visible;
}
*/
</style>
