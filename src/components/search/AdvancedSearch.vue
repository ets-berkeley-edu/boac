<template>
  <div class="align-center d-flex" role="search">
    <div class="mr-2">
      <label for="basic-search-input" class="sr-only">Search</label>
      <AccessibleCombobox
        :key="searchStore.autocompleteInputResetKey"
        :aria-description="`${labelForSearchInput()} (Type / to put focus in the search input field.)`"
        :clazz="{
          'text-medium-emphasis': !searchStore.queryText,
          'search-focus-in': searchStore.isFocusOnSearch || searchStore.queryText,
          'search-focus-out': !searchStore.isFocusOnSearch && !searchStore.queryText
        }"
        :disabled="searchStore.isSearching"
        :get-value="() => queryTextModel"
        id-prefix="basic-search"
        input-type="search"
        :is-busy="searchStore.isSearching"
        :items="searchStore.searchHistory"
        label="Search"
        list-label="Previous Search List"
        :menu-props="{'location': 'bottom'}"
        :on-submit="search"
        open-on-focus
        placeholder="/ to search"
        :when-item-selected="search"
        :set-value="v => queryTextModel = v"
      />
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
import AccessibleCombobox from '@/components/util/AccessibleCombobox'
import {addToSearchHistory, getMySearchHistory} from '@/api/search'
import {computed, onMounted, onUnmounted} from 'vue'
import {each, get, noop, trim} from 'lodash'
import {getAllTopics} from '@/api/topics'
import {labelForSearchInput} from '@/lib/search'
import {putFocusNextTick, scrollToTop} from '@/lib/utils'
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

onMounted(() => {
  document.addEventListener('keyup', onKeyUp, true)
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
    // forward slash key
    const el = get(event, 'currentTarget.activeElement')
    const ignore = ['textbox'].includes(get(el, 'role')) || ['INPUT'].includes(get(el, 'tagName'))
    if (!ignore) {
      putFocusNextTick('basic-search-input')
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
    addToSearchHistory(q).then(history => {
      searchStore.setSearchHistory(history)
    })
  } else {
    putFocusNextTick('basic-search-input')
  }
  scrollToTop()
}
</script>

<style scoped>
:deep(.search-focus-in) {
  border: 0;
  max-width: 300px;
  width: 300px;
  transition: max-width ease-out 0.2s;
}
:deep(.search-focus-out) {
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
