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
          autocomplete="off"
          bg-color="white"
          :class="{
            'text-grey': !queryText,
            'search-focus-in': isFocusOnSearch || queryText,
            'search-focus-out': !isFocusOnSearch && !queryText
          }"
          density="comfortable"
          :disabled="isSearching"
          hide-details
          hide-no-data
          :items="useSearchStore().searchHistory"
          :menu="isFocusOnSearch"
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
              :icon="mdiClose"
              size="x-small"
              @click="() => queryText = null"
            />
            <v-progress-circular
              v-if="isSearching"
              indeterminate
              size="x-small"
              width="2"
            />
          </template>
          <template #item="{index, item}">
            <v-list-item
              :id="`search-history-${index}`"
              class="font-size-18"
              @click="() => {
                queryText = item.value
                search()
              }"
            >
              {{ item.value }}
            </v-list-item>
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
            class="text-error"
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
import {alertScreenReader, putFocusNextTick, scrollToTop} from '@/lib/utils'
import {each, get, noop, trim} from 'lodash'

export default {
  name: 'AdvancedSearch',
  mixins: [Context, SearchSession],
  data: () => ({
    showErrorPopover: false
  }),
  mounted() {
    document.addEventListener('keyup', this.onKeyUp)
  },
  beforeUnmount() {
    document.removeEventListener('keyup', this.onKeyUp)
  },
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
    onKeyUp(event) {
      if (event.keyCode === 191) {
        const el = get(event, 'currentTarget.activeElement')
        const ignore = ['textbox'].includes(get(el, 'role')) || ['INPUT'].includes(get(el, 'tagName'))
        if (!ignore) {
          putFocusNextTick('search-students-input')
        }
      }
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
        alertScreenReader('Search input is required')
        putFocusNextTick('search-students-input')
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
</style>
