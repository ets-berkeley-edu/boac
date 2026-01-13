<template>
  <div class="align-center d-flex" role="search">
    <div class="on-surface mr-2">
      <AccessibleCombobox
        :key="searchStore.autocompleteInputResetKey"
        :aria-description="`${labelForSearchInput()} (Type / to put focus in the search input field.)`"
        :clazz="{
          'search-focus-in': searchStore.isFocusOnSearch || searchStore.queryText,
          'search-focus-out': !searchStore.isFocusOnSearch && !searchStore.queryText
        }"
        clearable
        :disabled="searchStore.isSearching"
        :get-value="() => queryTextModel"
        id-prefix="basic-search"
        input-type="search"
        :is-busy="searchStore.isSearching"
        :items="searchStore.searchHistory"
        label="Search"
        list-label="Previous Searches"
        :menu-props="{'location': 'bottom'}"
        :on-submit="search"
        :on-update-focused="isFocused => searchStore.setIsFocusOnSearch(isFocused)"
        open-on-focus
        placeholder="/ to search"
        :when-item-selected="search"
        :set-value="v => queryTextModel = v"
      />
    </div>
    <v-btn
      id="go-search"
      class="btn-search"
      :disabled="isSearchDisabled"
      text="Search"
      variant="outlined"
      @keydown.enter="search"
      @click.stop="search"
    />
    <AdvancedSearchModal v-if="(currentUser.canAccessAdvisingData || currentUser.canAccessCanvasData) && !isPeerAdvisor(currentUser)" />
  </div>
</template>

<script setup>
import {computed, onMounted, onUnmounted} from 'vue'
import {get, isEmpty, trim} from 'lodash'
import {useRoute, useRouter} from 'vue-router'
import AccessibleCombobox from '@/components/util/AccessibleCombobox'
import AdvancedSearchModal from '@/components/search/AdvancedSearchModal'
import {addToSearchHistory, getMySearchHistory} from '@/api/search'
import {labelForSearchInput} from '@/lib/search'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {useSearchStore} from '@/stores/search'
import {isPeerAdvisor} from '@/lib/boa-user.js'

const searchStore = useSearchStore()
const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const isSearchDisabled = computed(() => {
  const q = trim(searchStore.queryText)
  return searchStore.isSearching || isEmpty(q) || q === route.query.q
})
const queryTextModel = computed({
  get: () => searchStore.queryText || null,
  set: v => searchStore.setQueryText(v)
})
const route = useRoute()
const router = useRouter()

onMounted(() => {
  document.addEventListener('keyup', onKeyUp, true)
  searchStore.resetAdvancedSearch(route.query.q)
  getMySearchHistory().then(history => searchStore.setSearchHistory(history))
})

onUnmounted(() => {
  document.removeEventListener('keyup', onKeyUp)
})

const onKeyUp = event => {
  // Disable hot-key when, for example, user is editing a degree-progress note.
  const disableHotKey = useDegreeStore().disableButtons
  if (!disableHotKey && event.keyCode === 191) {
    // forward slash key
    const el = get(event, 'currentTarget.activeElement')
    const ignore = ['textbox'].includes(get(el, 'role')) || ['INPUT'].includes(get(el, 'tagName'))
    if (!ignore) {
      putFocusNextTick('basic-search-input')
    }
  }
}

const search = () => {
  if (!isSearchDisabled.value) {
    const q = trim(searchStore.queryText)
    if (q) {
      const searchPage = isPeerAdvisor(currentUser) ? {
        path: '/peer_advisor/search',
        query: {
          q: q
        }
      } : {
        path: '/search',
        query: {
          admits: currentUser.canAccessAdmittedStudents,
          courses: currentUser.canAccessCanvasData,
          notes: currentUser.canAccessAdvisingData,
          students: true,
          q
        }
      }
      searchStore.setIsSearching(true)
      router.push(searchPage)
      addToSearchHistory(q).then(history => {
        searchStore.setSearchHistory(history)
      })
    } else {
      putFocusNextTick('basic-search-input')
    }
  }
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
