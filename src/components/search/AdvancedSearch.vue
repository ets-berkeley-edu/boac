<template>
  <div class="justify-center d-flex">
    <div class="align-center d-flex">
      <div class="mr-2">
        <label for="search-students-input" class="sr-only">
          {{ labelForSearchInput() }}
          (Type / to put focus in the search input field.)
        </label>
        <v-combobox
          id="search-students-input"
          :key="searchStore.autocompleteInputResetKey"
          v-model="queryTextModel"
          aria-labelledby="search-input-label"
          autocomplete="off"
          bg-color="white"
          :class="{
            'text-grey': !searchStore.queryText,
            'search-focus-in': searchStore.isFocusOnSearch || searchStore.queryText,
            'search-focus-out': !searchStore.isFocusOnSearch && !searchStore.queryText
          }"
          density="comfortable"
          :disabled="searchStore.isSearching"
          hide-details
          hide-no-data
          :items="searchStore.searchHistory"
          :menu="searchStore.isFocusOnSearch"
          :menu-icon="null"
          :menu-props="{'attach': false, 'location': 'bottom'}"
          placeholder="/ to search"
          type="search"
          variant="outlined"
          @focusin="() => searchStore.setIsFocusOnSearch(true)"
          @focusout="() => searchStore.setIsFocusOnSearch(false)"
          @keydown.enter.prevent="search"
        >
          <template #append-inner>
            <v-btn
              v-if="!searchStore.isSearching && size(trim(searchStore.queryText))"
              aria-label="Clear search input"
              :icon="mdiClose"
              size="x-small"
              @click="() => searchStore.queryText = null"
            />
            <v-progress-circular
              v-if="searchStore.isSearching"
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
                searchStore.queryText = item.value
                search()
              }"
            >
              {{ item.value }}
            </v-list-item>
          </template>
        </v-combobox>
      </div>
      <v-btn
        v-if="currentUser.canAccessAdvisingData || currentUser.canAccessCanvasData"
        id="go-search"
        class="btn-search"
        :disabled="searchStore.isSearching"
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
import router from '@/router'
import {addToSearchHistory, getMySearchHistory} from '@/api/search'
import {computed, onMounted, onUnmounted} from 'vue'
import {each, get, noop, trim} from 'lodash'
import {getAllTopics} from '@/api/topics'
import {labelForSearchInput} from '@/lib/search'
import {mdiClose} from '@mdi/js'
import {putFocusNextTick, scrollToTop} from '@/lib/utils'
import {size} from 'lodash'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'
import {useSearchStore} from '@/stores/search'

const searchStore = useSearchStore()
const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const queryTextModel = computed({get: () => searchStore.queryText, set: v => searchStore.setQueryText(v)})

onMounted(() => {
  document.addEventListener('keyup', onKeyUp)
  searchStore.resetAdvancedSearch(useRoute().query.q)
  getMySearchHistory().then(history => {
    searchStore.setSearchHistory(history)
    if (currentUser.canAccessAdvisingData) {
      getAllTopics(true).then(rows => {
        const topicOptions = [{text: 'Any topic', value: null}]
        each(rows, row => {
          const topic = row['topic']
          topicOptions.push({
            text: topic,
            value: topic
          })
        })
        searchStore.setTopicOptions(topicOptions)
      })
    }
  })
})

onUnmounted(() => {
  document.removeEventListener('keyup', onKeyUp)
})

const onKeyUp = event => {
  if (event.keyCode === 191) {
    const el = get(event, 'currentTarget.activeElement')
    const ignore = ['textbox'].includes(get(el, 'role')) || ['INPUT'].includes(get(el, 'tagName'))
    if (!ignore) {
      putFocusNextTick('search-students-input')
    }
  }
}

const search = () => {
  const q = trim(searchStore.queryText)
  if (q) {
    router.push(
      {
        path: '/search',
        query: {
          admits: currentUser.canAccessAdmittedStudents,
          courses: currentUser.canAccessCanvasData,
          notes: currentUser.canAccessAdvisingData,
          students: true,
          q
        }
      },
      noop
    )
    addToSearchHistory(q).then(history => searchStore.setSearchHistory(history))
  } else {
    putFocusNextTick('search-students-input')
  }
  scrollToTop()
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
