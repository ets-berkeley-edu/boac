<template>
  <div class="align-center d-flex" role="search">
    <div class="mr-2">
      <label for="search-students-input" class="sr-only">Search</label>
      <v-combobox
        id="search-students-input"
        ref="searchInput"
        :key="searchStore.autocompleteInputResetKey"
        v-model="queryTextModel"
        :aria-label="`${labelForSearchInput()} (Type / to put focus in the search input field.)`"
        autocomplete="list"
        bg-color="white"
        :class="{
          'text-medium-emphasis': !searchStore.queryText,
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
        @update:focused="isFocused => isFocused ? searchStore.setIsFocusOnSearch(true) : noop"
        @update:menu="isOpen => !isOpen ? searchStore.setIsFocusOnSearch(false) : noop"
        @keydown.enter.prevent="search"
      >
        <template #append-inner>
          <v-btn
            v-if="!searchStore.isSearching && size(trim(searchStore.queryText))"
            aria-label="Clear search input"
            :icon="mdiClose"
            size="x-small"
            @click="onClearSearch"
            @keyup.enter="onClearSearch"
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
</template>

<script setup>
import AdvancedSearchModal from '@/components/search/AdvancedSearchModal'
import {addToSearchHistory, getMySearchHistory} from '@/api/search'
import {computed, nextTick, onMounted, onUnmounted, onUpdated, ref} from 'vue'
import {each, get, noop, size, trim} from 'lodash'
import {getAllTopics} from '@/api/topics'
import {labelForSearchInput} from '@/lib/search'
import {mdiClose} from '@mdi/js'
import {putFocusNextTick, scrollToTop, setComboboxAccessibleLabel} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useRoute, useRouter} from 'vue-router'
import {useSearchStore} from '@/stores/search'

const searchStore = useSearchStore()
const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const queryTextModel = computed({
  get: () => searchStore.queryText || null,
  set: v => searchStore.setQueryText(v)
})
const router = useRouter()
const searchInput = ref()

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

onUpdated(() => {
  nextTick(() => setComboboxAccessibleLabel(searchInput.value.$el, 'Search'))
})

const onClearSearch = () => {
  searchStore.queryText = null
  putFocusNextTick('search-students-input')
}

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
  color: rgb(var(--v-theme-surface));
  font-size: 16px;
  height: 46px;
  letter-spacing: 1px;
  padding: 6px 8px;
}
.btn-search:hover {
  background-color: rgb(var(--v-theme-surface));
  border-color: rgb(var(--v-theme-surface));
  color: rgb(var(--v-theme-primary));
}
</style>
